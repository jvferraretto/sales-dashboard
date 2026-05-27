$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")

Write-Host "Iniciando Backend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Title", "Backend - Sales Dashboard", "-Command", "cd 'c:\ClaudeCode\sales-dashboard\backend'; py -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 4

Write-Host "Iniciando Frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Title", "Frontend - Sales Dashboard", "-Command", "`$env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User'); cd 'c:\ClaudeCode\sales-dashboard\frontend'; npm run dev"

Start-Sleep -Seconds 2

Write-Host "Iniciando Ngrok..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Title", "Ngrok - Sales Dashboard", "-Command", "`$env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('PATH','User'); ngrok http 8000"

Write-Host ""
Write-Host "Tudo iniciado!" -ForegroundColor Green
Write-Host "Frontend:  http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend:   http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Settings:  http://localhost:3000/settings" -ForegroundColor Yellow
