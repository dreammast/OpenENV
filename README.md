# 🧠 OpenEnv — Education AI Track (Submission)

> **Reinforcement Learning for Adaptive Education** — A suite of three interactive environments designed to train AI agents in personalized tutoring, intensive coaching, and student retention strategies.

Built for the **Meta PyTorch × HuggingFace × Scalar Hackathon**.

---

## 📌 Project Status

| Component | Status | Description |
|-----------|--------|-------------|
| 🟢 Easy — Quiz Tutor | ✅ **Live** | Adaptive math tutoring (Zone of Proximal Development) |
| 🟡 Medium — Essay Coach | ✅ **Live** | Multi-dimensional essay feedback and revision |
| 🔴 Hard — Dropout Risk | ✅ **Live** | Weekly counselor interventions for at-risk students |
| 🤖 Gemini/Qwen Agent | ✅ **Ready** | Zero-shot baseline agent for all three tasks |
| 🐳 Docker Submission | ✅ **Verified** | Compliant with OpenEnv v1 specification |

---

## 🚀 Quick Start (Unified Server)

The project uses a modular server structure. All three environments are served from a single application entry point.

### 1. Setup Environment
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies (CPU optimized)
pip install -r requirements_local.txt
```

### 2. Launch the Environment Server
Set the difficulty level and start the server.
```powershell
# Options: easy, medium, hard
$env:TASK_DIFFICULTY="medium"
$env:PYTHONPATH="."
python -m openenv_core_submission.server.app --port 8000
```

### 3. Run the Baseline Agent
In a new terminal (with venv activated):
```powershell
# Provide your API key
$env:GEMINI_API_KEY = "your_key_here"

# Run the agent against the active server
python -m openenv_core_submission.server.agent_utils --task medium --port 8000
```

### 4. Optional: Visual Dashboard
Monitor the agent's performance in real-time via a web UI.
```powershell
# In a separate terminal
python dashboard/app.py
```
Then open **http://localhost:3000** in your browser.

---

## 🎯 The Three Environments

### 🟢 Easy — Adaptive Quiz Tutor
The agent acts as a **math tutor** selecting questions to maximize student learning.
- **State**: Per-topic mastery scores (fractions, algebra, geometry, statistics).
- **Actions**: Choose `topic` + `difficulty` (1-4) + `question_text`.
- **Primary Metric**: Mastery improvement across all topics.

### 🟡 Medium — Essay Feedback Coach
The agent is an **essay coach** providing targeted feedback to improve student writing quality.
- **State**: 5 quality dimensions (structure, grammar, content, creativity, coherence).
- **Actions**: Choose `feedback_type` + `focus_area` + `specificity` (1-3).
- **Primary Metric**: Cumulative improvement in essay quality scores.

### 🔴 Hard — Dropout Risk Counselor
The agent acts as a **counselor** choosing weekly interventions for students at risk of dropping out.
- **State**: Risk factors, GPA, attendance, and estimated dropout probability.
- **Actions**: Choose `intervention_type` + `intensity` (1-3) + `rationale`.
- **Primary Metric**: Student retention (did the student persist through the semester?).

---

## 📡 OpenEnv API Reference

All tasks are compliant with the OpenEnv v1 HTTP/WebSocket specification.

### Core Endpoints
- **`POST /reset`**: Initialize a new episode and receive the starting student profile.
- **`POST /step`**: Submit an action and receive the next observation, reward, and `done` flag.
- **`GET /state`**: Inspect the current internal state of the environment.

### Submission-Specific Endpoints
- **`GET /tasks`**: Returns the list of tasks and the Pydantic action/observation schemas.
- **`GET /grader`**: Returns the final normalized score (0.0 - 1.0) for the current episode.
- **`POST /baseline`**: Triggers a local inference run and returns the baseline score for validation.

---

## 🏗️ Submission & Docker

### Building the Image
```bash
docker build -t education-openenv:latest -f openenv_core_submission/server/Dockerfile .
```

### Deployment to Hugging Face
This repository is configured for direct deployment to HF Spaces using the `openenv` CLI.
```bash
cd openenv_core_submission
openenv push --repo-id your-username/education-ai-env
```

---

## 🏋️ Reinforcement Learning (RL) Training

You can train your own local agents using **GRPO (Group Relative Policy Optimization)**.

### 1. Run Training
Training a small LoRA adapter (rank 4) takes ~5-15 minutes on a modern CPU.
```powershell
# Options: train_easy.py, train_medium.py, train_hard.py
python train_medium.py
```
Checkpoints will be saved to `./checkpoints/`.

### 2. Monitor in Real-Time
You can visualize the RL agent's decisions as it trains or runs:
1. Start the Server: `$env:TASK_DIFFICULTY="medium"; python -m openenv_core_submission.server.app`
2. Start the Dashboard: `python dashboard/app.py`
3. Enable **"Monitor Mode"** in the Dashboard (checkbox).
4. Run the Agent: `python -m openenv_core_submission.server.agent_utils --task medium`

The dashboard will now "watch" the agent's moves and update the mastery bars and reward charts automatically!

---

## 📁 Project Structure
...
├── train_easy.py              # GRPO RL Training (Easy)
├── train_medium.py            # GRPO RL Training (Medium)
├── train_hard.py              # GRPO RL Training (Hard)
...

```
.
├── openenv_core_submission/
│   ├── server/
│   │   ├── app.py             # Main FastAPI Entry Point
│   │   ├── easy_env.py        # Quiz Tutor Logic
│   │   ├── medium_env.py      # Essay Coach Logic
│   │   ├── hard_env.py        # Dropout Risk Logic
│   │   ├── agent_utils.py     # Unified Agent/Baseline Logic
│   │   └── models.py          # Pydantic Schemas (Shared)
│   ├── openenv.yaml           # Submission Manifest
│   ├── client.py              # WebSocket Client Interface
│   └── Dockerfile             # Production Container Definition
├── dashboard/
│   ├── app.py                 # Dashboard Server (Port 3000)
│   └── index.html             # Visual Monitoring UI
├── README.md                  # This File (Single Source of Truth)
└── requirements_local.txt     # Local Development Dependencies
```

---

## 📜 License & Credits

Built for the **Meta PyTorch Hackathon** Education Track. Uses the `openenv[core]` framework.
