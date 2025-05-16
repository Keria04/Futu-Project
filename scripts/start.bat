@echo off
REM 切换到项目根目录
cd /d %~dp0\..

REM 检查 environment.yml 是否存在
if not exist environment.yml (
    echo Error: environment.yml not found in project root.
    pause
)

REM 检查 .conda 环境是否已存在
if not exist .conda (
    echo Creating conda environment at .\.conda ...
    call conda env create -f environment.yml -p .conda python=3.12.0
) else (
    echo Conda environment .\.conda already exists.
)

REM 激活当前目录下的 .conda 环境
call conda activate "%cd%\.conda"
if errorlevel 1 (
    echo Failed to activate conda environment.
    pause
)
echo Conda environment activated at .\.conda

REM 启动后端
cd backend
if exist app.py (
    echo Starting Flask application in new window...
    start "Flask Backend" cmd /k "conda activate %cd%\..\ .conda && python app.py"
) else (
    echo Error: app.py not found in backend directory.
    pause
)

REM 启动前端
cd ..\frontend
if exist package.json (
    echo Installing npm packages...
    call npm install
    if errorlevel 1 (
        echo Failed to install npm packages.
        pause
    )
    echo Starting Vite frontend in new window...
    start "Vite Frontend" cmd /k "conda activate %cd%\..\ .conda && npm run dev"
) else (
    echo Error: package.json not found in frontend directory.
    exit /b 1
)

REM 启动完成，主脚本直接退出
echo All services started. You may close this window.
