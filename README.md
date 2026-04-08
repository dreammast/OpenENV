---
title: OpenEnv - Education AI Training
emoji: 🧠
colorFrom: blue
colorTo: green
sdk: docker
app_file: dashboard/app.py
pinned: false
---

# OpenEnv — Education AI Training Platform

> **Adaptive Education through Reinforcement Learning** — Train AI agents to personalize education delivery across three interactive learning environments: quiz tutoring, essay coaching, and dropout risk intervention.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**🚀 [Live on Hugging Face Spaces](https://huggingface.co/spaces/dreammast/OpenENV)** | **📚 [GitHub Repository](https://github.com/dreammast/OpenENV)** | **📄 [GitHub Pages](https://dreammast.github.io/OpenENV/)**

---

## 🎯 Overview

OpenEnv is a comprehensive framework for training AI agents in personalized education. It provides three carefully-designed learning environments that simulate real educational scenarios:

| Environment | Task | Objective | Complexity |
|-------------|------|-----------|-----------|
| **🟢 Easy** | Quiz Tutor | Maximize student mastery across math topics | Foundational |
| **🟡 Medium** | Essay Coach | Improve multi-dimensional writing quality | Intermediate |
| **🔴 Hard** | Dropout Counselor | Retain at-risk students through targeted intervention | Advanced |

Each environment includes:
- ✅ **Realistic Simulations**: Student behavior models with learning dynamics
- ✅ **Real-time Feedback**: Immediate reward signals for RL training
- ✅ **Interactive Dashboard**: Monitor agent performance and decisions
- ✅ **Metrics Tracking**: Success rates, mastery convergence, efficiency scores
- ✅ **Docker Ready**: One-command deployment to any platform

---

## 🚀 Quick Start

### Option 1: Cloud Deployment (Recommended)
**Access live on Hugging Face Spaces** (no installation needed):
👉 [**Open OpenEnv on Spaces**](https://huggingface.co/spaces/dreammast/OpenENV)

### Option 2: Local Development

#### Prerequisites
- Python 3.11+
- Docker (optional, for containerized deployment)
- Git

#### Installation
```bash
# Clone repository
git clone https://github.com/dreammast/OpenENV.git
cd OpenENV

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### Launch Services
```bash
# Terminal 1: Start API Server (port 8000)
export TASK_DIFFICULTY=easy  # Options: easy, medium, hard
python -m openenv_core_submission.server.app

# Terminal 2: Start Dashboard (port 3000)
export DASHBOARD_PORT=3000
python dashboard/app.py

# Terminal 3: Open browser
# Navigate to: http://localhost:3000
```

#### Run Training
```bash
# Train on a specific environment
python train_easy.py      # Quiz Tutor
python train_medium.py    # Essay Coach
python train_hard.py      # Dropout Counselor
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    OpenEnv Platform                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐         ┌──────────────────┐     │
│  │  Interactive     │         │  FastAPI Server  │     │
│  │  Dashboard       │◄───────►│  (Port 8000)     │     │
│  │  (Port 3000)     │ HTTP    │                  │     │
│  └──────────────────┘         ├──────────────────┤     │
│          │                    │  • Easy Env      │     │
│          │                    │  • Medium Env    │     │
│          │                    │  • Hard Env      │     │
│          │                    └──────────────────┘     │
│          │                                              │
│    Real-time Metrics                  Reward Signals  │
│    • Success Rate                     • RL Training    │
│    • Mastery Convergence             • Agent Learning │
│    • Performance Analytics                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Core Components

**`openenv_core_submission/`** - Main API Server
- `server/app.py` - FastAPI application entry point
- `server/easy_env.py` - Quiz tutoring environment
- `server/medium_env.py` - Essay coaching environment
- `server/hard_env.py` - Dropout risk intervention environment
- `models.py` - Pydantic data schemas

**`dashboard/`** - Interactive Monitoring UI
- `app.py` - Dashboard server
- `index.html` - Real-time visualization & controls

**`openenv/`** - Core RL Framework
- Complete OpenEnv v1 specification implementation
- HTTP server & client interfaces
- Environment abstractions

---

## 📊 Features

### 🎓 Three Educational Environments

#### 🟢 Easy — Adaptive Quiz Tutor
*Maximize student math mastery through intelligent topic selection*

**State Space:**
- Per-topic mastery scores (fractions, algebra, geometry, statistics)
- Difficulty history for each topic
- Student learning rate

**Action Space:**
- Topic selection (4 choices)
- Difficulty level (1-4)
- Question presentation

**Reward Signal:**
- +0.3 for correct answers
- +0.2 bonus for appropriate difficulty
- Topic diversity bonus
- Cumulative mastery progress

---

#### 🟡 Medium — Essay Feedback Coach
*Improve writing quality across multiple dimensions*

**State Space:**
- 5 quality dimensions: structure, grammar, content, creativity, coherence
- Receptivity to feedback
- Improvement trajectory

**Action Space:**
- Feedback type (6 types: reorg, grammar, deepening, creativity, coherence, thesis)
- Specificity level (1-3)
- Focus area targeting

**Reward Signal:**
- Improvement in targeted dimensions
- Adaptive diminishing returns for repeated feedback
- Weak spot targeting bonus

---

#### 🔴 Hard — Dropout Risk Counselor
*Retain at-risk students through targeted interventions*

**State Space:**
- 5 risk factors: academic struggle, financial stress, social isolation, mental health, attendance
- Root cause identification
- GPA and engagement metrics

**Action Space:**
- Intervention type (8 types: tutoring, financial aid, mental health, peer mentor, etc.)
- Intensity level (1-3)
- Timing optimization

**Reward Signal:**
- Risk factor reduction
- Root cause intervention bonus
- Resource efficiency tracking
- Student persistence metric

---

### 📈 Real-time Monitoring Dashboard

**Live Metrics:**
- 📊 Success Rate - Accuracy of agent decisions
- 📈 Mastery Convergence - Learning progress visualization
- ⚡ Efficiency Score - Reward per action
- 🎯 Strategy Selector - 4 agent modes (Adaptive/Progressive/Balanced/Conservative)

**Interactive Controls:**
- ▶️ Run Episode - Single training iteration
- 🔄 Auto-Run 3 - Execute 3 episodes sequentially
- 📊 Real-time Charts - Reward trends & convergence tracking
- 💬 Decision Logging - View agent reasoning for each action

---

### 🤖 RL Training Framework

**Built-in Training Scripts:**
```bash
python train_easy.py      # LoRA-based RL on Quiz Tutor
python train_medium.py    # RL on Essay Coach
python train_hard.py      # RL on Dropout Counselor
```

**Supported Methods:**
- Group Relative Policy Optimization (GRPO)
- Experience replay with reward weighting
- Multi-episode evaluation
- Checkpoint management

---

## 📡 API Reference

### Core Endpoints

**`POST /reset`** - Initialize new episode
```json
Request: {}
Response: {
  "episode_id": "uuid",
  "observation": {...},
  "done": false,
  "reward": 0.0
}
```

**`POST /step`** - Execute action
```json
Request: {
  "episode_id": "uuid",
  "action": {
    "topic": "algebra",
    "difficulty": 2,
    "question_text": "Solve: 2x + 3 = 7"
  }
}
Response: {
  "observation": {...},
  "reward": 0.45,
  "done": false,
  "info": {...}
}
```

**`GET /health`** - Server status
```json
Response: {
  "status": "healthy",
  "task": "easy",
  "port": 8000,
  "version": "1.0.0"
}
```

**`GET /tasks`** - Available environments
```json
Response: {
  "available_tasks": ["easy", "medium", "hard"],
  "schemas": {...}
}
```

---

## 🐳 Docker Deployment

### Build Locally
```bash
docker build -t openenv:latest .
```

### Run Container
```bash
docker run -p 8000:8000 -p 3000:3000 \
  -e TASK_DIFFICULTY=easy \
  openenv:latest
```

### Deploy to Hugging Face Spaces
```bash
git push -f hf master:main
```

### Deploy to GitHub
```bash
git push -u github master:main
```

---

## 📚 Usage Examples

### Example 1: Run a Single Episode
```python
import requests
import json

# Reset environment
reset_resp = requests.post("http://localhost:8000/reset")
episode_id = reset_resp.json()["episode_id"]
observation = reset_resp.json()["observation"]

# Step with action
action = {
    "topic": "algebra",
    "difficulty": 2,
    "question_text": "Example question"
}
step_resp = requests.post(
    "http://localhost:8000/step",
    json={"episode_id": episode_id, "action": action}
)

print(f"Reward: {step_resp.json()['reward']}")
print(f"Done: {step_resp.json()['done']}")
```

### Example 2: Train Agent Automatically
```bash
# Via interactive dashboard
# 1. Open http://localhost:3000
# 2. Click "▶ Run Episode" to run single episode
# 3. Click "🔄 Auto-Run 3" to run 3 episodes
# 4. Watch metrics and charts update in real-time
```

---

## 📈 Performance Metrics

**Typical Training Results:**
- **Easy**: 70%+ accuracy by episode 5
- **Medium**: 60%+ quality improvement by episode 10
- **Hard**: 55%+ intervention effectiveness by episode 8

**Monitoring via Dashboard:**
- Success rate trends
- Mastery convergence curves
- Per-episode reward analysis
- Strategy effectiveness comparison

---

## 🛠️ Customization

### Add Custom Strategy
Edit `dashboard/index.html` `agentDecideEasy()` function:
```javascript
function agentDecideEasy(obs, episodeNum = 1) {
    // Your custom logic here
    return {
        topic: selectedTopic,
        difficulty: selectedDifficulty,
        question_text: "Custom question",
        reason: "My strategy reason"
    };
}
```

### Modify Reward Function
Edit environment files:
- `openenv_core_submission/server/easy_env.py`
- `openenv_core_submission/server/medium_env.py`
- `openenv_core_submission/server/hard_env.py`

---

## 📋 Project Structure

```
OpenENV/
├── openenv_core_submission/        # Main API
│   ├── server/
│   │   ├── app.py                 # FastAPI entry point
│   │   ├── easy_env.py            # Quiz tutor
│   │   ├── medium_env.py          # Essay coach
│   │   ├── hard_env.py            # Dropout counselor
│   │   └── agent_utils.py         # Agent logic
│   ├── models.py                  # Data schemas
│   └── Dockerfile
├── dashboard/                      # UI
│   ├── app.py                     # Dashboard server
│   └── index.html                 # Web interface
├── openenv/                        # Core framework
│   └── core/
│       ├── env_server/            # HTTP server
│       └── env_client.py          # Client
├── train_easy.py                  # RL training
├── train_medium.py
├── train_hard.py
├── Dockerfile                      # Production image
├── docker-compose.yml             # Multi-container
├── requirements.txt               # Dependencies
└── README.md                       # This file
```

---

## 🚀 Deployment

### Quick Deploy to Hugging Face Spaces
```bash
# 1. Create space at https://huggingface.co/spaces
# 2. Clone this repo and push
git remote add hf https://huggingface.co/spaces/dreammast/OpenENV.git
git push -f hf master:main
```

### Deploy to GitHub
```bash
git remote add github https://github.com/dreammast/OpenENV.git
git push -u github master:main
```

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- [ ] Additional RL training algorithms
- [ ] More education scenarios
- [ ] Performance optimizations
- [ ] Mobile dashboard support
- [ ] Multi-agent support
- [ ] Enhanced visualizations

**To contribute:**
1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see LICENSE file for details.

Built for the **Meta PyTorch × HuggingFace × Scalar Hackathon**.

---

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/dreammast/OpenENV/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dreammast/OpenENV/discussions)
- **Live Demo**: [Hugging Face Spaces](https://huggingface.co/spaces/dreammast/OpenENV)

---

## 🙏 Acknowledgments

- OpenEnv framework & specification
- Meta PyTorch Hackathon organizers
- HuggingFace Spaces platform
- Educational AI community

---

<div align="center">

**[⬆ back to top](#openenv--education-ai-training-platform)**

Made with ❤️ for education

</div>
