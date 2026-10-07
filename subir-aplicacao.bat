@echo off
REM clinica-saas - subir aplicacao MODO TRADICIONAL local
REM Postgres local Windows + Redis via WSL + Backend Django :8000 + Frontend Next.js :3000
REM Uso: duplo-clique ou .\subir-aplicacao.bat
setlocal EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"

set BACKEND_DIR=backend
set FRONTEND_DIR=frontend
set VENV_DIR=%BACKEND_DIR%\.venv
set PSQL=C:\Program Files\PostgreSQL\18\bin\psql.exe
set BACKEND_URL=http://localhost:8000/api/v1/
set FRONTEND_URL=http://localhost:3000

echo.
echo [1/6] Checando node + python + psql...
where node >nul 2>nul
if errorlevel 1 goto :fail_node
where python >nul 2>nul
if errorlevel 1 goto :fail_python
if not exist "%PSQL%" goto :fail_psql
echo OK: node + python + psql encontrados.

echo.
echo [2/6] Garantindo backend\.env...
if not exist "%BACKEND_DIR%\.env" goto :fail_noenv
echo OK: backend\.env existe.

echo.
echo [3/6] Postgres local...
call :pg_ensure
echo.
echo [4/6] Redis via WSL...
call :redis_ensure

echo.
echo [5/6] Backend: venv + requirements + migrate...
if not exist "%VENV_DIR%\Scripts\python.exe" goto :venv_create
goto :venv_ok
:venv_create
echo Criando venv...
python -m venv "%VENV_DIR%"
if errorlevel 1 goto :fail_venv
:venv_ok
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r "%BACKEND_DIR%\requirements.txt"
if errorlevel 1 goto :fail_pip
echo Aplicando migrations...
python "%BACKEND_DIR%\manage.py" migrate_schemas --noinput
if errorlevel 1 goto :fail_migrate

echo.
echo [6/6] Frontend: npm install quando preciso...
if not exist "%FRONTEND_DIR%\node_modules" goto :npm_install
echo node_modules ja existe.
goto :open_windows
:npm_install
pushd "%FRONTEND_DIR%"
call npm install --legacy-peer-deps
if errorlevel 1 goto :fail_npm
popd

:open_windows
echo.
echo Abrindo Backend :8000 e Frontend :3000 em janelas separadas...
start "clinica-backend :8000" cmd /k "cd /d ""%~dp0%BACKEND_DIR%"" && ""%~dp0%VENV_DIR%\Scripts\activate.bat"" && python manage.py runserver 0.0.0.0:8000"
start "clinica-frontend :3000" cmd /k "cd /d ""%~dp0%FRONTEND_DIR%"" && set ""NEXT_PUBLIC_API_URL=%BACKEND_URL%"" && set ""NEXT_PUBLIC_API_BASE=http://localhost:8000"" && npm run dev"

echo.
echo Pronto:
echo - Backend: http://localhost:8000/api/v1/
echo - Frontend: %FRONTEND_URL%
echo - Ver logs backend e frontend nas janelas abertas.
endlocal
goto :eof

:pg_ensure
"%PSQL%" -h 127.0.0.1 -U postgres -tc "SELECT 1" >nul 2>nul
if errorlevel 1 goto :pg_start_service
goto :pg_role
:pg_start_service
echo Postgres local nao respondeu. Tentando iniciar o servico...
net start postgresql-x64-18 >nul 2>nul
"%PSQL%" -h 127.0.0.1 -U postgres -tc "SELECT 1" >nul 2>nul
if errorlevel 1 goto :fail_pg
:pg_role
"%PSQL%" -h 127.0.0.1 -U postgres -v ON_ERROR_STOP=1 -c "DO $do$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='clinica') THEN CREATE ROLE clinica LOGIN PASSWORD 'clinica_dev_only'; END IF; END $do$;" -c "ALTER ROLE clinica WITH CREATEDB LOGIN;"
if errorlevel 1 goto :fail_pg
"%PSQL%" -h 127.0.0.1 -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='clinica'" | findstr 1 >nul
if errorlevel 1 goto :pg_createdb
goto :pg_done
:pg_createdb
"%PSQL%" -h 127.0.0.1 -U postgres -v ON_ERROR_STOP=1 -c "CREATE DATABASE clinica OWNER clinica;"
if errorlevel 1 goto :fail_pg
:pg_done
echo OK: Postgres local com role e database clinica.
exit /b 0

:redis_ensure
wsl -d Ubuntu -- bash -c "test -x ~/.local/redis/usr/bin/redis-server"
if errorlevel 1 goto :redis_install
goto :redis_ping
:redis_install
echo Instalando redis local no WSL, sem sudo...
wsl -d Ubuntu -- bash -c "mkdir -p ~/.local/redis && cd /tmp && rm -f redis_*.deb redis-server_*.deb redis-tools_*.deb liblzf1_*.deb libjemalloc2_*.deb && apt-get download redis redis-server redis-tools liblzf1 libjemalloc2 && dpkg-deb -x redis-server_*.deb ~/.local/redis && dpkg-deb -x redis_*.deb ~/.local/redis && dpkg-deb -x redis-tools_*.deb ~/.local/redis && dpkg-deb -x liblzf1_*.deb ~/.local/redis && dpkg-deb -x libjemalloc2_*.deb ~/.local/redis"
if errorlevel 1 goto :fail_redis
:redis_ping
wsl -d Ubuntu -- bash -c "export LD_LIBRARY_PATH=~/.local/redis/usr/lib/x86_64-linux-gnu; ~/.local/redis/usr/bin/redis-cli -p 6379 ping"
if errorlevel 1 goto :redis_start
goto :redis_ok
:redis_start
echo Iniciando redis no WSL...
wsl -d Ubuntu -- bash -c "export LD_LIBRARY_PATH=~/.local/redis/usr/lib/x86_64-linux-gnu; ~/.local/redis/usr/bin/redis-server --daemonize yes --port 6379"
if errorlevel 1 goto :fail_redis
wsl -d Ubuntu -- bash -c "export LD_LIBRARY_PATH=~/.local/redis/usr/lib/x86_64-linux-gnu; ~/.local/redis/usr/bin/redis-cli -p 6379 ping"
if errorlevel 1 goto :fail_redis
:redis_ok
echo OK: redis respondendo na 6379.
exit /b 0

:fail_node
echo [ERRO] Node nao encontrado. Instale o Node 20+.
pause
exit /b 1
:fail_python
echo [ERRO] Python nao encontrado. Instale o Python 3.13+.
pause
exit /b 1
:fail_psql
echo [ERRO] psql nao encontrado em C:\Program Files\PostgreSQL\18\bin. Ajuste PSQL no script.
pause
exit /b 1
:fail_noenv
echo [ERRO] backend\.env nao existe. Copie de backend\.env.example.
pause
exit /b 1
:fail_pg
echo [ERRO] Postgres local falhou. Verifique o servico postgresql-x64-18.
pause
exit /b 1
:fail_redis
echo [ERRO] Redis no WSL falhou. Verifique rede para archive.ubuntu.com e o WSL.
pause
exit /b 1
:fail_venv
echo [ERRO] Falha ao criar venv.
pause
exit /b 1
:fail_pip
echo [ERRO] pip install falhou.
pause
exit /b 1
:fail_migrate
echo [ERRO] migrate_schemas falhou. Veja o erro acima.
pause
exit /b 1
:fail_npm
echo [ERRO] npm install falhou.
popd
pause
exit /b 1
