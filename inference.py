#!/usr/bin/env python3
"""
Inference.py - Baseline Inference Script for OpenEnv Education Track

This script:
1. Connects to the running OpenEnv server
2. Runs complete episodes for all 3 tasks (easy, medium, hard)
3. Uses the Groq API (with OpenAI fallback) for agent decisions
4. Returns normalized scores (0.0-1.0) for each task

Usage:
    python inference.py --task medium --port 8000
    python inference.py --mode all  # Run all 3 tasks
"""

import os
import json
import argparse
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class InferenceAgent:
    """Base agent for running inference on education environments"""
    
    def __init__(self, use_llm: bool = True):
        """Initialize with Groq or OpenAI API (fallback to heuristics if unavailable)"""
        self.use_llm = use_llm
        self.use_groq = False
        self.step_counter = 0
        
        if not use_llm:
            print("[OK] Using heuristic-based agent (no LLM required)")
            return
        
        # Try OpenAI first
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model_name = os.environ.get("OPENAI_MODEL", "gpt-4")
        
        # Groq fallback
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.groq_base_url = os.environ.get("GROQ_API_BASE", "https://api.groq.com/openai/v1")
        self.groq_model = os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768")
        
        if not self.api_key and not self.groq_api_key:
            print("[WARN] No API keys found. Falling back to heuristics.")
            self.use_llm = False
            return
        
        # Initialize client
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                print("[OK] Using OpenAI: {}".format(self.model_name))
            except Exception as e:
                print("[WARN] OpenAI failed: {}".format(e))
                self._switch_to_groq()
        else:
            self._switch_to_groq()
    
    def _switch_to_groq(self):
        """Switch to Groq fallback"""
        if not self.groq_api_key:
            print("[WARN] Groq API key not available. Falling back to heuristics.")
            self.use_llm = False
            return
        self.use_groq = True
        self.client = OpenAI(api_key=self.groq_api_key, base_url=self.groq_base_url)
        self.model_name = self.groq_model
        print("[FALLBACK] Switched to Groq: {}".format(self.model_name))
    
    def get_action_heuristic(self, task: str, obs: dict) -> dict:
        """Generate action using heuristics (no LLM required)"""
        self.step_counter += 1
        
        if task == "easy":
            # Quiz tutor heuristic
            topics = ["fractions", "algebra", "geometry", "statistics"]
            topic = topics[self.step_counter % len(topics)]
            
            # Adjust difficulty based on feedback
            reward = obs.get("reward", 0.0)
            turns_left = obs.get("turns_remaining", 8)
            base_difficulty = max(1, min(4, 2 + int(reward * 2)))
            
            return {
                "topic": topic,
                "difficulty": base_difficulty,
                "question_text": "Question: {}".format(self.step_counter)
            }
        
        elif task == "medium":
            # Essay coach heuristic
            feedback_types = ["grammar_correction", "clarity_improvement", "structure_feedback"]
            focus_areas = ["grammar", "clarity", "content"]
            feedback_type = feedback_types[self.step_counter % len(feedback_types)]
            focus_area = focus_areas[self.step_counter % len(focus_areas)]
            
            return {
                "feedback_type": feedback_type,
                "focus_area": focus_area,
                "specificity": max(1, min(3, 1 + (self.step_counter // 4)))
            }
        
        else:  # hard
            # Dropout counselor heuristic
            intervention_types = ["academic_tutoring", "mentorship", "financial_aid"]
            intervention_type = intervention_types[self.step_counter % len(intervention_types)]
            
            return {
                "intervention_type": intervention_type,
                "intensity": max(1, min(3, 1 + (self.step_counter // 3))),
                "rationale": "Support step {}".format(self.step_counter)
            }
    
    def get_action(self, prompt: str, task: str = "medium", obs: dict = None) -> dict:
        """Call LLM to get next action, with heuristic fallback"""
        if not self.use_llm or obs is None:
            return self.get_action_heuristic(task, obs or {})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            text = response.choices[0].message.content
            
            # Extract JSON from response
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print("[WARN] LLM call failed: {}. Using heuristics.".format(str(e)[:50]))
            # Try Groq fallback if using OpenAI
            if not self.use_groq and self.groq_api_key:
                print("[FALLBACK] Attempting Groq fallback...")
                self._switch_to_groq()
                if self.use_llm:
                    try:
                        return self.get_action(prompt, task, obs)
                    except Exception as groq_error:
                        print("[WARN] Groq also failed. Using heuristics.")
            
            # Fall back to heuristics
            return self.get_action_heuristic(task, obs or {})


# Prompt templates
PROMPTS = {
    "easy": """You are a Math Tutor. Analyze the student's mastery scores.
State: {state}
Output ONLY valid JSON: {{"topic": "fractions", "difficulty": 2, "question_text": "What is 1/2 + 1/4?"}}""",
    
    "medium": """You are an Essay Feedback Coach. Analyze essay quality.
State: {state}
Output ONLY valid JSON: {{"feedback_type": "grammar_correction", "focus_area": "grammar", "specificity": 2}}""",
    
    "hard": """You are a University Counselor. Identify root cause from risk factors.
State: {state}
Output ONLY valid JSON: {{"intervention_type": "academic_tutoring", "intensity": 2, "rationale": "Low GPA"}}"""
}


def run_episode(task: str, port: int = 8000, max_steps: int = 10) -> dict:
    """Run a single episode and return results"""
    agent = InferenceAgent()
    base_url = "http://127.0.0.1:{}".format(port)
    
    print("\n" + "="*60)
    print("Running {} Task".format(task.upper()))
    print("="*60)
    
    # Reset environment
    try:
        reset_res = requests.post("{}/reset".format(base_url), timeout=10).json()
    except Exception as e:
        print("[ERROR] Failed to connect to server: {}".format(e))
        return {
            "task": task,
            "status": "error",
            "error": str(e),
            "score": 0.0
        }
    
    obs = reset_res if "student_profile" in reset_res else reset_res.get("observation", {})
    done = reset_res.get("done", False)
    total_reward = 0.0
    step_count = 0
    
    # Episode loop
    while not done and step_count < max_steps:
        step_count += 1
        
        # Get action from LLM or heuristics
        prompt = PROMPTS[task].format(state=json.dumps(obs, indent=2))
        action = agent.get_action(prompt, task, obs)
        
        if not action:
            print("[WARN] Failed to get action at step {}".format(step_count))
            break
        
        print("Step {}: {}".format(step_count, action))
        
        # Submit action
        try:
            step_res = requests.post(
                "{}/step".format(base_url),
                json={"action": action},
                timeout=10
            ).json()
        except Exception as e:
            print("[ERROR] Step failed: {}".format(e))
            break
        
        obs = step_res if "student_profile" in step_res else step_res.get("observation", {})
        reward = step_res.get("reward", 0.0)
        done = step_res.get("done", False)
        total_reward += reward
        
        print("  Reward: {:+.3f} | Total: {:+.3f}".format(reward, total_reward))
        time.sleep(0.3)
    
    # Get final grade
    try:
        grade_res = requests.get("{}/grader".format(base_url), timeout=10).json()
        final_score = grade_res.get("score", 0.0)
    except:
        final_score = max(0.0, min(1.0, total_reward / 10.0))
    
    print("\n[OK] {} Complete".format(task.upper()))
    print("   Total Reward: {:+.3f}".format(total_reward))
    print("   Final Score: {:.3f}".format(final_score))
    
    return {
        "task": task,
        "status": "success",
        "total_reward": round(total_reward, 3),
        "final_score": round(final_score, 3),
        "steps": step_count
    }


def run_all_tasks(port: int = 8000) -> dict:
    """Run all 3 tasks"""
    results = {}
    for task in ["easy", "medium", "hard"]:
        results[task] = run_episode(task, port)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run inference baseline on OpenEnv education tasks"
    )
    parser.add_argument(
        "--task",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Task to run (default: medium)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    parser.add_argument(
        "--mode",
        choices=["single", "all"],
        default="single",
        help="Run single task or all tasks"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=10,
        help="Max steps per episode"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("OpenEnv Education Track - Baseline Inference")
    print("="*60)
    
    if args.mode == "all":
        results = run_all_tasks(args.port)
    else:
        results = run_episode(args.task, args.port, args.max_steps)
    
    # Print summary
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    if isinstance(results, dict) and "task" in results:
        results = {results["task"]: results}
    
    for task, result in results.items():
        status = "[OK]" if result.get("status") == "success" else "[ERR]"
        score = result.get("final_score", 0.0)
        print("{} {:8s} | Score: {:6.3f}".format(status, task, score))
    
    # Validate scores
    print("\n" + "="*60)
    print("VALIDATION")
    print("="*60)
    for task, result in results.items():
        score = result.get("final_score", 0.0)
        if 0.0 <= score <= 1.0:
            print("[OK] {:8s} | Score in range [0.0, 1.0]".format(task))
        else:
            print("[ERR] {:8s} | Score {} OUT OF RANGE".format(task, score))
    
    return results


if __name__ == "__main__":
    results = main()
    success_count = sum(1 for r in (results.values() if isinstance(results, dict) and "task" not in results else [results]) 
                       if r.get("status") == "success")
    exit(0 if success_count > 0 else 1)
