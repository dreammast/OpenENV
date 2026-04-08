@echo off
REM =============================================================================
REM  OpenEnv Education Track — One-Click Demo Runner
REM  Runs on 8GB RAM, NO GPU, NO Docker
REM =============================================================================
REM
REM  Usage:
REM    run_demo.bat easy     — Run easy environment training demo
REM    run_demo.bat hard     — Run hard environment training demo
REM    run_demo.bat setup    — Install dependencies only
REM    run_demo.bat servers  — Start env servers only
REM =============================================================================

title OpenEnv Demo

if "%1"=="setup" goto :setup
if "%1"=="easy" goto :easy
if "%1"=="hard" goto :hard
if "%1"=="med_api" goto :med_api
if "%1"=="hard_api" goto :hard_api
if "%1"=="servers" goto :servers

echo.
echo  ╔═══════════════════════════════════════════════════╗
echo  ║   OpenEnv Education Track — Demo Runner           ║
echo  ║   CPU-only · 8GB RAM · No Docker                  ║
echo  ╚═══════════════════════════════════════════════════╝
echo.
echo  Usage:
echo    run_demo.bat setup     Install dependencies
echo    run_demo.bat easy      Train on Easy env (Local)
echo    run_demo.bat med_api   Run Medium env (Gemini API)
echo    run_demo.bat hard_api  Run Hard env (Gemini API)
echo    run_demo.bat servers   Start all env servers
echo.
goto :end

:setup
echo.
echo [SETUP] Creating virtual environment...
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [SETUP] Installing CPU-only dependencies...
pip install -r requirements_local.txt
echo.
echo [SETUP] Done! Now run: run_demo.bat easy
goto :end

:servers
echo.
echo [SERVERS] Starting environment servers...
call venv\Scripts\activate.bat
echo Starting Easy server on :8001...
start "Easy Env (8001)" cmd /k "call venv\Scripts\activate.bat && python envs\easy_server.py"
echo Starting Hard server on :8003...
start "Hard Env (8003)" cmd /k "call venv\Scripts\activate.bat && python envs\hard_server.py"
echo.
echo Servers starting in new windows. Wait 5 seconds then run training.
goto :end

:easy
echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║  EASY — Adaptive Quiz Tutor (Demo)                ║
echo ╚═══════════════════════════════════════════════════╝
call venv\Scripts\activate.bat
echo.
echo [1/3] Starting Easy environment server...
start "Easy Env (8001)" cmd /k "call venv\Scripts\activate.bat && python envs\easy_server.py"
echo       Waiting 5 seconds for server to start...
timeout /t 5 /nobreak > nul
echo [2/3] Checking server health...
curl -sf http://localhost:8001/health > nul 2>&1
if errorlevel 1 (
    echo       Server not ready yet, waiting 5 more seconds...
    timeout /t 5 /nobreak > nul
)
echo [3/3] Starting training...
echo.
python train_easy.py
echo.
echo Done! Check checkpoints\easy-quiz-grpo-lora\ for the LoRA adapter.
goto :end

:hard
echo.
echo ╔═══════════════════════════════════════════════════╗
echo ║  HARD — Dropout Risk Intervention (Demo)          ║
echo ╚═══════════════════════════════════════════════════╝
call venv\Scripts\activate.bat
echo.
echo [1/3] Starting Hard environment server...
start "Hard Env (8003)" cmd /k "call venv\Scripts\activate.bat && python envs\hard_server.py"
echo       Waiting 5 seconds for server to start...
timeout /t 5 /nobreak > nul
echo [2/3] Checking server health...
curl -sf http://localhost:8003/health > nul 2>&1
if errorlevel 1 (
    echo       Server not ready yet, waiting 5 more seconds...
    timeout /t 5 /nobreak > nul
)
echo [3/3] Starting training...
echo.
python train_hard.py
echo.
echo Done! Check checkpoints\hard-dropout-grpo-lora\ for the LoRA adapter.
goto :end

:med_api
echo.
echo [1/3] Starting Medium environment server...
start "Medium Env (8002)" cmd /k "call venv\Scripts\activate.bat && python envs\medium_server.py"
timeout /t 5 /nobreak > nul
echo [2/3] Running Gemini API Agent...
call venv\Scripts\activate.bat
python run_api_agent.py medium
goto :end

:hard_api
echo.
echo [1/3] Starting Hard environment server...
start "Hard Env (8003)" cmd /k "call venv\Scripts\activate.bat && python envs\hard_server.py"
timeout /t 5 /nobreak > nul
echo [2/3] Running Gemini API Agent...
call venv\Scripts\activate.bat
python run_api_agent.py hard
goto :end

:end
