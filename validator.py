#!/usr/bin/env python3
"""
Validator.py - Pre-Submission Validation Script

Validates:
1. openenv.yaml format and specification compliance
2. Environment endpoints (reset, step, state, grader)
3. Response schemas and score ranges
4. Environment variables
5. Model configurations

Usage:
    python validator.py --port 8000
    python validator.py --full  # Run all validation checks
"""

import os
import yaml
import json
import requests
import sys
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

class ValidationError(Exception):
    """Custom validation error"""
    pass


class OpenEnvValidator:
    """Validates OpenEnv specification compliance"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.base_url = "http://127.0.0.1:{}".format(port)
        self.errors = []
        self.warnings = []
        self.passed = []
    
    def add_error(self, msg: str):
        """Record validation error"""
        self.errors.append("[ERROR] {}".format(msg))
    
    def add_warning(self, msg: str):
        """Record validation warning"""
        self.warnings.append("[WARN] {}".format(msg))
    
    def add_pass(self, msg: str):
        """Record passed validation"""
        self.passed.append("[OK] {}".format(msg))
    
    # =========================================================================
    # 1. OPENENV.YAML VALIDATION
    # =========================================================================
    
    def validate_openenv_yaml(self) -> bool:
        """Validate openenv.yaml structure and content"""
        print("\n" + "="*70)
        print("CHECKING: openenv.yaml Format")
        print("="*70)
        
        try:
            with open("openenv_core_submission/openenv.yaml", "r") as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            self.add_error("openenv.yaml not found at openenv_core_submission/openenv.yaml")
            return False
        except yaml.YAMLError as e:
            self.add_error("openenv.yaml parse error: {}".format(e))
            return False
        
        # Check required fields
        required_fields = ["spec_version", "name", "type", "runtime", "app", "port", "tasks"]
        for field in required_fields:
            if field not in config:
                self.add_error("Missing required field: {}".format(field))
            else:
                self.add_pass("Found {}: {}".format(field, config[field]))
        
        # Validate spec_version
        if config.get("spec_version") != 1:
            self.add_warning("spec_version is {}, expected 1".format(config.get('spec_version')))
        
        # Validate runtime
        if config.get("runtime") != "fastapi":
            self.add_error("runtime must be 'fastapi', got '{}'".format(config.get('runtime')))
        
        # Validate app entry point
        if not config.get("app"):
            self.add_error("app entry point not specified")
        elif ":" not in config.get("app", ""):
            self.add_error("Invalid app format: '{}' (should be 'module:app')".format(config.get('app')))
        else:
            self.add_pass("App entry point valid: {}".format(config.get('app')))
        
        # Validate port
        port = config.get("port")
        if not isinstance(port, int) or port < 1 or port > 65535:
            self.add_error("Invalid port: {}".format(port))
        else:
            self.add_pass("Port valid: {}".format(port))
        
        # Validate tasks
        tasks = config.get("tasks", [])
        if not isinstance(tasks, list) or len(tasks) < 3:
            self.add_error("Must have at least 3 tasks, found {}".format(len(tasks)))
        else:
            task_ids = [t.get("id") for t in tasks]
            self.add_pass("Found 3+ tasks: {}".format(task_ids))
            
            if "easy" not in task_ids or "medium" not in task_ids or "hard" not in task_ids:
                self.add_warning("Expected tasks: easy, medium, hard")
        
        return len(self.errors) == 0
    
    # =========================================================================
    # 2. ENVIRONMENT VARIABLES VALIDATION
    # =========================================================================
    
    def validate_env_variables(self) -> bool:
        """Validate required environment variables"""
        print("\n" + "="*70)
        print("CHECKING: Environment Variables")
        print("="*70)
        
        required_vars = [
            ("GROQ_API_KEY", "Groq API key (required for inference fallback)"),
            ("GROQ_MODEL", "Groq model name"),
            ("HF_TOKEN", "HuggingFace token")
        ]
        
        optional_vars = [
            ("OPENAI_API_KEY", "OpenAI API key (optional, uses Groq fallback)"),
            ("OPENAI_MODEL", "OpenAI model name"),
        ]
        
        all_found = True
        for var, description in required_vars:
            value = os.environ.get(var)
            if value:
                self.add_pass("{} is set".format(var))
            else:
                self.add_error("{} not set - {}".format(var, description))
                all_found = False
        
        for var, description in optional_vars:
            value = os.environ.get(var)
            if value:
                self.add_pass("{} is set (optional)".format(var))
            else:
                self.add_warning("{} not set - {}".format(var, description))
        
        return all_found
    
    # =========================================================================
    # 3. SERVER CONNECTIVITY VALIDATION
    # =========================================================================
    
    def validate_server_connectivity(self) -> bool:
        """Verify server is running and responsive"""
        print("\n" + "="*70)
        print("CHECKING: Server Connectivity")
        print("="*70)
        
        try:
            response = requests.get("{}/tasks".format(self.base_url), timeout=5)
            if response.status_code == 200:
                self.add_pass("Server responding on {}".format(self.base_url))
                return True
            else:
                self.add_error("Server returned {} instead of 200".format(response.status_code))
                return False
        except requests.exceptions.ConnectionError:
            self.add_error("Cannot connect to server at {}".format(self.base_url))
            self.add_warning("Make sure server is running: python -m openenv_core_submission.server.app")
            return False
        except Exception as e:
            self.add_error("Connection error: {}".format(e))
            return False
    
    # =========================================================================
    # 4. ENDPOINT VALIDATION
    # =========================================================================
    
    def validate_endpoints(self) -> bool:
        """Validate all required endpoints exist and respond correctly"""
        print("\n" + "="*70)
        print("CHECKING: API Endpoints")
        print("="*70)
        
        endpoints = [
            ("GET", "/tasks", "List tasks and schemas"),
            ("POST", "/reset", "Reset environment"),
            ("GET", "/state", "Get current state (requires reset first)"),
        ]
        
        all_valid = True
        
        # Test endpoints that don't require state
        for method, endpoint, description in endpoints[:2]:
            try:
                if method == "GET":
                    resp = requests.get("{}{}".format(self.base_url, endpoint), timeout=5)
                else:
                    resp = requests.post("{}{}".format(self.base_url, endpoint), timeout=5)
                
                if resp.status_code == 200:
                    self.add_pass("{} {} -> 200 OK ({})".format(method, endpoint, description))
                else:
                    self.add_error("{} {} -> {} (expected 200)".format(method, endpoint, resp.status_code))
                    all_valid = False
            except Exception as e:
                self.add_error("{} {} failed: {}".format(method, endpoint, e))
                all_valid = False
        
        # Test /step and /grader (need reset first)
        try:
            requests.post("{}/reset".format(self.base_url), timeout=5)
            
            # Test /step with a dummy action
            step_resp = requests.post(
                "{}/step".format(self.base_url),
                json={"action": {"topic": "algebra", "difficulty": 2}},
                timeout=5
            )
            if step_resp.status_code == 200:
                self.add_pass("POST /step -> 200 OK")
            else:
                self.add_error("POST /step -> {}".format(step_resp.status_code))
                all_valid = False
            
            # Test /grader
            grader_resp = requests.get("{}/grader".format(self.base_url), timeout=5)
            if grader_resp.status_code == 200:
                self.add_pass("GET /grader -> 200 OK")
            else:
                self.add_error("GET /grader -> {}".format(grader_resp.status_code))
                all_valid = False
        except Exception as e:
            self.add_error("Dynamic endpoint test failed: {}".format(e))
            all_valid = False
        
        return all_valid
    
    # =========================================================================
    # 5. RESPONSE SCHEMA VALIDATION
    # =========================================================================
    
    def validate_schemas(self) -> bool:
        """Validate API response schemas"""
        print("\n" + "="*70)
        print("CHECKING: Response Schemas")
        print("="*70)
        
        try:
            # Get task schemas
            tasks_resp = requests.get("{}/tasks".format(self.base_url)).json()
            
            if "tasks" not in tasks_resp:
                self.add_error("GET /tasks missing 'tasks' field")
                return False
            
            if "action_schema" not in tasks_resp:
                self.add_error("GET /tasks missing 'action_schema'")
                return False
            
            if "observation_schema" not in tasks_resp:
                self.add_error("GET /tasks missing 'observation_schema'")
                return False
            
            self.add_pass("GET /tasks has all required fields")
            
            # Test observation structure
            reset_resp = requests.post("{}/reset".format(self.base_url)).json()
            if "student_profile" in reset_resp:
                self.add_pass("Observation contains 'student_profile'")
            elif "observation" in reset_resp:
                self.add_warning("Using generic 'observation' wrapper")
            else:
                self.add_warning("Observation structure non-standard")
            
            return True
        except Exception as e:
            self.add_error("Schema validation failed: {}".format(e))
            return False
    
    # =========================================================================
    # 6. GRADER VALIDATION
    # =========================================================================
    
    def validate_grader(self) -> bool:
        """Validate grader returns scores in correct range"""
        print("\n" + "="*70)
        print("CHECKING: Grader (Scoring)")
        print("="*70)
        
        try:
            # Run a full episode
            requests.post("{}/reset".format(self.base_url))
            
            for i in range(5):
                requests.post(
                    "{}/step".format(self.base_url),
                    json={"action": {"topic": "algebra", "difficulty": 2}}
                )
            
            # Check grader
            grader_resp = requests.get("{}/grader".format(self.base_url)).json()
            score = grader_resp.get("score")
            
            if score is None:
                self.add_error("Grader response missing 'score' field")
                return False
            
            if not isinstance(score, (int, float)):
                self.add_error("Score is not numeric: {}".format(type(score)))
                return False
            
            if 0.0 <= score <= 1.0:
                self.add_pass("Score in valid range [0.0, 1.0]: {:.3f}".format(score))
                return True
            else:
                self.add_error("Score out of range [0.0, 1.0]: {}".format(score))
                return False
        except Exception as e:
            self.add_error("Grader validation failed: {}".format(e))
            return False
    
    # =========================================================================
    # 7. INFERENCE SCRIPT VALIDATION
    # =========================================================================
    
    def validate_inference_script(self) -> bool:
        """Verify inference.py exists and is executable"""
        print("\n" + "="*70)
        print("CHECKING: Inference Script")
        print("="*70)
        
        if not os.path.exists("inference.py"):
            self.add_error("inference.py not found in root directory")
            return False
        
        self.add_pass("inference.py exists")
        
        # Check if it's readable
        try:
            with open("inference.py", "r") as f:
                content = f.read()
                if "def run_episode" in content:
                    self.add_pass("inference.py contains run_episode() function")
                else:
                    self.add_warning("inference.py missing run_episode() function")
                
                if "parser = argparse" in content:
                    self.add_pass("inference.py has argument parsing")
                else:
                    self.add_warning("inference.py missing argument parsing")
            
            return True
        except Exception as e:
            self.add_error("Cannot read inference.py: {}".format(e))
            return False
    
    # =========================================================================
    # MAIN VALIDATION RUNNER
    # =========================================================================
    
    def run_all(self) -> Tuple[int, int, int]:
        """Run all validations and return (passed, warnings, errors)"""
        print("\n")
        print("=" * 70)
        print("OpenEnv Pre-Submission Validator")
        print("=" * 70)
        
        # Run all validations
        self.validate_openenv_yaml()
        self.validate_env_variables()
        server_ok = self.validate_server_connectivity()
        
        if server_ok:
            self.validate_endpoints()
            self.validate_schemas()
            self.validate_grader()
        else:
            self.add_warning("Skipping endpoint tests (server not running)")
        
        self.validate_inference_script()
        
        # Print results
        print("\n" + "="*70)
        print("VALIDATION REPORT")
        print("="*70)
        
        print("\nPASSED:")
        for msg in self.passed:
            print("  {}".format(msg))
        
        if self.warnings:
            print("\nWARNINGS:")
            for msg in self.warnings:
                print("  {}".format(msg))
        
        if self.errors:
            print("\nERRORS:")
            for msg in self.errors:
                print("  {}".format(msg))
        
        # Summary
        print("\n" + "="*70)
        total = len(self.passed) + len(self.warnings) + len(self.errors)
        print("SUMMARY: {} passed, {} warnings, {} errors".format(
            len(self.passed), len(self.warnings), len(self.errors)
        ))
        
        if self.errors:
            print("FAILED - fix errors before submission")
            return len(self.passed), len(self.warnings), len(self.errors)
        elif self.warnings:
            print("PASSED with warnings")
            return len(self.passed), len(self.warnings), len(self.errors)
        else:
            print("PASSED - ready for submission!")
            return len(self.passed), len(self.warnings), len(self.errors)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Pre-submission validation for OpenEnv Education Track"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run all validation checks"
    )
    
    args = parser.parse_args()
    
    validator = OpenEnvValidator(args.port)
    passed, warnings, errors = validator.run_all()
    
    # Exit with appropriate code
    exit(0 if errors == 0 else 1)


if __name__ == "__main__":
    main()
