# 🚀 Deployment Guide

Deploy **OpenEnv** to Hugging Face Spaces and GitHub Pages using GitHub Actions.

## Prerequisites

- GitHub account with repository access
- Hugging Face account
- Git installed locally

---

## Step 1: Create GitHub Repository

```bash
# Initialize git in your project
cd e:\env_agent
git init
git add .
git commit -m "Initial commit: OpenEnv education AI"

# Add remote origin
git remote add origin https://github.com/dreammast/OpenENV.git
git branch -M main
git push -u origin main
```

---

## Step 2: Set Up Hugging Face Space

### Option A: Automatic (via GitHub Actions)
1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Name: `OpenENV`
4. Type: **Docker** (for full backend support)
5. Click "Create Space"

### Option B: Manual Setup
```bash
# Clone the HF space repo
git clone https://huggingface.co/spaces/dreammast/OpenENV
cd OpenENV

# Copy files from GitHub
cp -r /path/to/github/repo/* .

# Commit and push
git add .
git commit -m "Deploy OpenEnv"
git push
```

---

## Step 3: Configure GitHub Secrets

For automatic deployment, add these secrets to your GitHub repository:

1. Go to **Settings → Secrets and variables → Actions**
2. Add new secret: `HF_TOKEN`
   - Value: Your Hugging Face API token from [settings/tokens](https://huggingface.co/settings/tokens)
3. Add new secret: `HF_SPACE_ID`
   - Value: `dreammast/OpenENV`

---

## Step 4: Enable GitHub Pages

1. Go to **Settings → Pages**
2. Set source to **GitHub Actions**
3. Deploy automatically on push to main

---

## Step 5: Deploy

### Via GitHub Actions (Recommended)
- Push changes to `main` branch
- GitHub Actions automatically deploys to:
  - ✅ Hugging Face Spaces
  - ✅ GitHub Pages

### Manual Push to Hugging Face

```bash
# Add HF remote
git remote add hf https://huggingface.co/spaces/dreammast/OpenENV

# Force push (HF spaces)
git push -f hf main:main
```

---

## 📍 Access Your Deployment

Once deployed:

- **Hugging Face Spaces**: `https://huggingface.co/spaces/dreammast/OpenENV`
- **GitHub Pages**: `https://dreammast.github.io/OpenENV/`

---

## 🐳 Docker Deployment

The `Dockerfile` automatically:
- Installs Python 3.11
- Installs dependencies from `requirements.txt`
- Runs both API server (port 8000) and Dashboard (port 3000)
- Exposes both ports for reverse proxy

---

## Environment Variables

Configure these in your deployment:

```env
TASK_DIFFICULTY=easy          # easy, medium, or hard
DASHBOARD_PORT=3000           # Dashboard server port
PORT=8000                      # API server port
GROQ_API_KEY=your_key_here    # LLM API key (optional)
```

---

## Monitoring & Logs

### GitHub Actions
- View logs: **Actions** tab → Latest workflow run

### Hugging Face Spaces
- View logs: Space page → **Logs** tab
- Restart: Click restart button

### GitHub Pages
- View build: **Actions** tab → **pages build and deployment**

---

## Troubleshooting

### HF Space shows "Building..."
-Wait 5-10 minutes for Docker build
- Check **Logs** tab for errors

### GitHub Pages not updating
- Push to `main` branch (not `master`)
- Check **Settings → Pages** source is set to **GitHub Actions**

### API not responding
- Verify ports 8000 and 3000 are exposed
- Check Docker build logs
- Review API health: `https://spaces/api/easy/health`

---

## Next Steps

1. ✅ Set up GitHub repository
2. ✅ Create Hugging Face Space
3. ✅ Add GitHub Secrets
4. ✅ Enable GitHub Pages
5. ✅ Push code to trigger deployment
6. ✅ Visit your deployed application!

---

For questions or issues, check:
- [Hugging Face Spaces Docs](https://huggingface.co/docs/hub/spaces)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
