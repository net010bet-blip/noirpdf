@echo off
setlocal
cd /d "%~dp0"
where docker >nul 2>nul
if errorlevel 1 (
  echo Instale e inicie o Docker Desktop antes de executar o NoirPDF.
  pause
  exit /b 1
)
if not exist .env powershell -NoProfile -Command "$b=New-Object byte[] 32;[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b);$s=[Convert]::ToBase64String($b).TrimEnd('=').Replace('+','-').Replace('/','_');$t=[regex]::Replace([IO.File]::ReadAllText('.env.example'),'(?m)^POSTGRES_PASSWORD=.*$',('POSTGRES_PASSWORD='+$s));[IO.File]::WriteAllText('.env',$t,(New-Object Text.UTF8Encoding $false))"
if not exist .env (
  echo Nao foi possivel criar .env. Copie .env.example e configure POSTGRES_PASSWORD.
  pause
  exit /b 1
)
docker compose up --build -d --wait --wait-timeout 180
if errorlevel 1 (
  echo Nao foi possivel iniciar. Confira se o Docker esta aberto e se a porta 3000 esta livre.
  echo Para diagnostico: docker compose logs --tail 100
  pause
  exit /b 1
)
start "" http://localhost:3000
echo NoirPDF pronto. Para encerrar: docker compose down
pause
