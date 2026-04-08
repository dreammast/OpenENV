#!/usr/bin/env bash
# =============================================================================
# quickstart.sh — OpenEnv Education Track
# Meta PyTorch × HuggingFace × Scalar Hackathon
# =============================================================================
# Usage:
#   chmod +x scripts/quickstart.sh
#   ./scripts/quickstart.sh           # full interactive setup
#   ./scripts/quickstart.sh --check   # pre-flight checks only
#   ./scripts/quickstart.sh --down    # stop and remove all containers
# =============================================================================

set -euo pipefail

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }
step()    { echo -e "\n${BOLD}${BLUE}▶ $*${NC}"; }

# ── Arg parsing ───────────────────────────────────────────────────────────────
MODE="start"
case "${1:-}" in
  --check) MODE="check" ;;
  --down)  MODE="down"  ;;
  --train-easy)   MODE="train-easy"   ;;
  --train-medium) MODE="train-medium" ;;
  --train-hard)   MODE="train-hard"   ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# ── Banner ────────────────────────────────────────────────────────────────────
echo -e "
${BOLD}${BLUE}╔══════════════════════════════════════════════════════════╗
║   OpenEnv Education Track — Hackathon Quickstart         ║
║   Meta PyTorch × HuggingFace × Scalar                   ║
╚══════════════════════════════════════════════════════════╝${NC}

  🟢  Easy   → Adaptive Quiz Tutor           :8001
  🟡  Medium → Essay Feedback Coach          :8002
  🔴  Hard   → Dropout Risk Intervention     :8003
  🏋️  Trainer → GRPO via TRL (GPU)
"

# =============================================================================
# PRE-FLIGHT CHECKS
# =============================================================================
preflight() {
  step "Pre-flight checks"

  # Docker
  if ! command -v docker &>/dev/null; then
    error "Docker not found. Install from https://docs.docker.com/get-docker/"
  fi
  success "Docker $(docker --version | awk '{print $3}' | tr -d ',')"

  # Docker Compose
  if ! docker compose version &>/dev/null; then
    error "Docker Compose v2 not found. Update Docker Desktop or install compose plugin."
  fi
  success "Docker Compose $(docker compose version --short)"

  # .env file
  if [[ ! -f ".env" ]]; then
    warn ".env not found — copying .env.example"
    cp .env.example .env
    warn "⚠️  Edit .env and set HF_TOKEN before training."
  else
    success ".env found"
  fi

  # HF_TOKEN check (only warn, don't block env servers)
  if grep -q "REPLACE_WITH_YOUR_TOKEN" .env 2>/dev/null; then
    warn "HF_TOKEN is still the placeholder value in .env"
    warn "Set a real token before running: docker compose run trainer python training/train_easy.py"
  else
    success "HF_TOKEN looks set in .env"
  fi

  # GPU check (optional — env servers don't need GPU)
  if command -v nvidia-smi &>/dev/null; then
    GPU=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    success "GPU detected: ${GPU}"
  else
    warn "nvidia-smi not found — GPU training will not be available"
    warn "Env servers (easy/medium/hard) run on CPU and don't need a GPU."
  fi

  # Ports free
  for port in 8001 8002 8003; do
    if lsof -i ":${port}" &>/dev/null 2>&1 || ss -tlnp "sport = :${port}" 2>/dev/null | grep -q LISTEN; then
      warn "Port ${port} may already be in use"
    else
      success "Port ${port} is free"
    fi
  done

  echo ""
  success "Pre-flight complete."
}

# =============================================================================
# START ENV SERVERS
# =============================================================================
start_envs() {
  step "Building and starting environment servers"
  info "This pulls base images and installs deps — takes ~2 min on first run."
  echo ""

  docker compose up --build -d easy-env medium-env hard-env

  step "Waiting for health checks to pass..."
  for service in easy-env medium-env hard-env; do
    port=$(docker compose port "$service" "$(docker compose config --format json 2>/dev/null | python3 -c "
import sys, json
cfg = json.load(sys.stdin)
svc = cfg.get('services', {}).get('$service', {})
ports = svc.get('ports', [])
print(ports[0].get('target', '8001') if ports else '8001')
" 2>/dev/null || echo "8001")")

    echo -n "  Waiting for ${service}..."
    for i in $(seq 1 30); do
      if curl -sf "http://localhost:${port}/health" &>/dev/null; then
        echo -e " ${GREEN}healthy${NC} ✓"
        break
      fi
      if [[ $i -eq 30 ]]; then
        echo -e " ${RED}timed out${NC}"
        warn "Check logs: docker compose logs ${service}"
      fi
      sleep 2
      echo -n "."
    done
  done
}

# =============================================================================
# SMOKE TEST
# =============================================================================
smoke_test() {
  step "Smoke tests — calling /reset on each environment"

  for cfg in "8001:Easy (Adaptive Quiz Tutor)" "8002:Medium (Essay Feedback Coach)" "8003:Hard (Dropout Risk Intervention)"; do
    port="${cfg%%:*}"
    name="${cfg#*:}"
    echo -n "  ${name}... "
    response=$(curl -sf -X POST "http://localhost:${port}/reset" \
      -H "Content-Type: application/json" \
      -d '{}' 2>&1 || echo "FAILED")
    if echo "$response" | grep -q "done\|observation\|feedback\|dropout_risk" 2>/dev/null; then
      echo -e "${GREEN}OK${NC} ✓"
    else
      echo -e "${YELLOW}unexpected response — env may still be starting${NC}"
    fi
  done
}

# =============================================================================
# PRINT SUMMARY
# =============================================================================
print_summary() {
  echo -e "
${BOLD}${GREEN}═══════════════════════════════════════════════════════════
  ✅  All environment servers are running!
═══════════════════════════════════════════════════════════${NC}

${BOLD}Endpoints${NC}
  🟢  Easy   (Adaptive Quiz)    →  http://localhost:8001
  🟡  Medium (Essay Coach)      →  http://localhost:8002
  🔴  Hard   (Dropout Risk)     →  http://localhost:8003

${BOLD}OpenAPI Docs${NC}
  http://localhost:8001/docs
  http://localhost:8002/docs
  http://localhost:8003/docs

${BOLD}Next steps${NC}
  # Start training (Easy tier):
  docker compose run --rm trainer python training/train_easy.py

  # Start training (Medium tier):
  docker compose run --rm trainer python training/train_medium.py

  # Start training (Hard tier):
  docker compose run --rm trainer python training/train_hard.py

  # Interactive trainer shell:
  docker compose run --rm trainer bash

  # Follow logs:
  docker compose logs -f easy-env
  docker compose logs -f trainer

  # Scale to 4 replicas of Easy env + Envoy load balancer:
  docker compose --profile scale up --scale easy-env=4

  # Stop everything:
  docker compose down

${BOLD}Monitoring${NC}
  docker compose ps               — service status
  docker compose stats            — live resource usage
  docker compose logs -f          — all logs
"
}

# =============================================================================
# MAIN
# =============================================================================
case "$MODE" in
  check)
    preflight
    ;;
  down)
    step "Stopping all containers"
    docker compose --profile dashboard --profile scale down
    success "All containers stopped."
    ;;
  train-easy)
    preflight
    step "Starting trainer for Easy environment"
    docker compose run --rm trainer python training/train_easy.py
    ;;
  train-medium)
    preflight
    step "Starting trainer for Medium environment"
    docker compose run --rm trainer python training/train_medium.py
    ;;
  train-hard)
    preflight
    step "Starting trainer for Hard environment"
    docker compose run --rm trainer python training/train_hard.py
    ;;
  start)
    preflight
    start_envs
    smoke_test
    print_summary
    ;;
esac
