# 📋 Deployment Checklist

## ✅ Pre-Deployment (Local)

- [ ] **Test locally** - Run episode and verify accuracy increasing
  ```bash
  python -m openenv_core_submission.server.app  # Terminal 1
  python dashboard/app.py                       # Terminal 2
  Visit: http://localhost:3000
  ```

- [ ] **Test Docker build** - Verify Docker builds without errors
  ```bash
  docker build -t openenv:latest .
  docker-compose up -d
  ```

- [ ] **Check all files created**:
  - `Dockerfile`
  - `docker-compose.yml`
  - `requirements.txt`
  - `.gitignore`
  - `.github/workflows/deploy.yml`
  - `app.yml` (HF Spaces config)
  - `DEPLOYMENT.md`

---

## 🚀 Deployment Steps

### Step 1: Initialize Git Repository
```bash
cd e:\env_agent
git init
git add .
git commit -m "Initial commit: OpenEnv education AI training dashboard"
```

### Step 2: Create GitHub Repository
1. Go to [GitHub](https://github.com/new)
2. Repository name: `OpenENV`
3. Description: `Reinforcement Learning for Adaptive Education`
4. Make it **Public** (for GitHub Pages)
5. Click "Create repository"

### Step 3: Push to GitHub
```bash
git remote add origin https://github.com/dreammast/OpenENV.git
git branch -M main
git push -u origin main
```

### Step 4: Create Hugging Face Space
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Space name: `OpenENV`
4. License: **OpenRAIL-M**
5. SDK: **Docker**
6. Click "Create Space"

### Step 5: Add GitHub Secrets (for auto-deployment)
**GitHub Settings → Secrets and variables → Actions**

Add these secrets:
```
HF_TOKEN = <your-huggingface-api-token>
HF_SPACE_ID = dreammast/OpenENV
```

Get your HF token from: https://huggingface.co/settings/tokens

### Step 6: Enable GitHub Pages
**GitHub Settings → Pages**
- Source: **GitHub Actions**
- Auto-deploy on push to `main` branch

### Step 7: Manual Deploy to HF Spaces (if auto doesn't work)
```bash
git remote add hf https://huggingface.co/spaces/dreammast/OpenENV
git push -f hf main:main
```

---

## 📍 Access Deployed Apps

Once deployment completes (5-10 minutes):

| Platform | URL |
|----------|-----|
| 🤗 Hugging Face Spaces | `https://huggingface.co/spaces/dreammast/OpenENV` |
| 📄 GitHub Pages | `https://dreammast.github.io/OpenENV/` |
| 💻 GitHub Repo | `https://github.com/dreammast/OpenENV` |

---

## 🔍 Verify Deployment

### Hugging Face Spaces
1. Visit space URL
2. Wait for Docker build (5-10 min)
3. Check **Logs** tab if building
4. Click **Run** once built

### GitHub Pages
1. Visit GitHub Pages URL
2. Dashboard HTML should load
3. Check **Settings → Pages** for status

### GitHub Actions
1. Go to **Actions** tab
2. View latest workflow run
3. Check for ✅ or ❌ status

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **HF Space stuck on "Building"** | Wait 10+ minutes; check Logs tab for errors |
| **GitHub Pages shows 404** | Push to `main` branch; wait 1-2 minutes; check Settings → Pages |
| **API responding slow** | May be cold-start on HF Spaces; takes 30-60s first request |
| **Docker build fails** | Check `requirements.txt` dependencies; run locally first |
| **GitHub Actions fails** | Check workflow logs; verify HF_TOKEN secret is set correctly |

---

## 📝 Next Steps

After deployment:

1. **Share your space** on social media / forums
2. **Monitor performance** - check logs regularly
3. **Train the model** - run episodes on deployed dashboard
4. **Collect metrics** - track accuracy improvement over time
5. **Iterate** - push improvements to GitHub → auto-redeploy

---

## 🎯 Quick Command Reference

```bash
# Local testing
docker-compose up -d              # Start locally
docker-compose logs -f            # View logs
docker-compose down               # Stop services

# GitHub
git add .
git commit -m "..."
git push origin main              # Triggers all deployments

# HF Spaces (manual)
git remote add hf https://huggingface.co/spaces/dreammast/OpenENV
git push -f hf main:main          # Force push to spaces

# View status
git remote -v                      # See all remotes
docker images | grep openenv      # See Docker images
docker ps                          # See running containers
```

---

**You're all set! 🎉 Your OpenEnv AI training dashboard is ready to deploy!**
