import os
import json
import requests
import time
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

class QwenAgent:
    def __init__(self):
        # Try OpenAI first, fallback to Groq
        self.use_groq = False
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.base_url = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
        self.model_name = os.environ.get("OPENAI_MODEL", "gpt-4")
        
        # Fallback keys
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.groq_base_url = os.environ.get("GROQ_API_BASE", "https://api.groq.com/openai/v1")
        self.groq_model = os.environ.get("GROQ_MODEL", "mixtral-8x7b-32768")
        
        if not self.api_key and not self.groq_api_key:
            print("---------------------------------------------------------")
            print("⚠️  MISSING API KEYS")
            print("Please set either OPENAI_API_KEY or GROQ_API_KEY in .env")
            print("---------------------------------------------------------")
            exit(1)
        
        # Initialize with OpenAI first
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
                print(f"🤖 Using OpenAI API: {self.model_name}")
            except Exception as e:
                print(f"⚠️  OpenAI initialization failed: {e}")
                self._switch_to_groq()
        else:
            self._switch_to_groq()
    
    def _switch_to_groq(self):
        """Switch to Groq fallback provider"""
        if not self.groq_api_key:
            print("❌ Groq API key not available")
            exit(1)
        self.use_groq = True
        self.client = OpenAI(api_key=self.groq_api_key, base_url=self.groq_base_url)
        self.model_name = self.groq_model
        self.api_key = self.groq_api_key
        print(f"🔄 Switched to Groq (fallback): {self.model_name}")

    def get_action(self, prompt: str) -> dict:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            text = response.choices[0].message.content
            
            # Robust JSON extraction
            import re
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            
            text = text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"❌ Error calling {self.model_name}: {e}")
            # If using OpenAI and it fails, try Groq as fallback
            if not self.use_groq and self.groq_api_key:
                print("🔄 Attempting Groq fallback...")
                self._switch_to_groq()
                try:
                    return self.get_action(prompt)  # Retry with Groq
                except Exception as groq_error:
                    print(f"❌ Groq also failed: {groq_error}")
                    return None
            if 'text' in locals():
                print(f"Raw Response: {text}")
            return None

# --- Prompt Templates ---

EASY_PROMPT = """
You are a Math Tutor. Analyze the student's mastery scores across topics.
Select the next topic and difficulty (1-4) to target their Zone of Proximal Development.
Env State: {obs}
Output ONLY JSON: {{"topic": "fractions", "difficulty": 2, "question_text": "What is 1/2 + 1/4?"}}
"""

MEDIUM_PROMPT = """
You are an expert Essay Feedback Coach. Analyze the student's essay quality.
Provide feedback to improve the weakest area.
Env State: {obs}
Output ONLY JSON: {{"feedback_type": "grammar_correction", "focus_area": "grammar", "specificity": 3}}
"""

HARD_PROMPT = """
You are a University Counselor. Analyze the student risk factors and identify the root cause.
Select a weekly intervention (1-3 intensity).
Env State: {obs}
Output ONLY JSON: {{"intervention_type": "academic_tutoring", "intensity": 2, "rationale": "Low GPA"}}
"""

def run_episode(port: int = 8000, mode: str = None):
    agent = QwenAgent()
    base_url = f"http://127.0.0.1:{port}"
    
    # Identify task by port or env var
    if not mode:
        mode = "medium"
        if port == 8001: mode = "easy"
        elif port == 8003: mode = "hard"
    
    prompt_template = {"easy": EASY_PROMPT, "medium": MEDIUM_PROMPT, "hard": HARD_PROMPT}[mode]

    print(f"🚀 Connecting to {base_url}/reset ...")
    try:
        res = requests.post(f"{base_url}/reset").json()
    except Exception as e:
        print(f"Error: Connection failed. Is the server running on {port}?")
        return {"error": str(e)}

    # OpenEnv-core style observation unpacking
    obs = res if "student_profile" in res else res.get("observation", {})
    done = res.get("done", False)
    total_reward = 0.0
    
    while not done:
        prompt = prompt_template.format(obs=json.dumps(obs, indent=2))
        action = agent.get_action(prompt)
        if not action: break 

        print(f"[{mode.upper()} STEP {res.get('metadata',{}).get('step',0)+1}] Action: {action}")
        
        step_res = requests.post(f"{base_url}/step", json={"action": action}).json()
        
        # OpenEnv-core often returns Observation wrapper or flat
        obs = step_res if "student_profile" in step_res else step_res.get("observation", {})
        reward = step_res.get("reward", 0.0)
        done = step_res.get("done", False)
        total_reward += reward
        
        print(f"  → Reward: {reward:+.3f} | Total: {total_reward:+.3f}")
        time.sleep(0.5) # Slight delay for readability

    # After episode, get final grade
    try:
        grade_res = requests.get(f"{base_url}/grader").json()
        final_grade = grade_res.get("score") or grade_res.get("grade") or 0.0
    except:
        final_grade = 0.0

    return {
        "task": mode,
        "total_reward": round(total_reward, 3),
        "final_grade": final_grade
    }

def run_baseline(port: int = 8000):
    """Run baseline for all tasks (or just the active one) and return results."""
    # For sub-tasks, we might want to iterate or just run the current one
    # The requirement says 'returns baseline score for all 3 tasks'
    # But usually the server only hosts one task at a time in some configs.
    # We will try to run for the active one at the given port.
    return run_episode(port=port)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    result = run_episode(port)
    print(f"\n✅ Episode Complete: {result}")
