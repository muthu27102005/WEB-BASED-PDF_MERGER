Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "          PDF Merger Flask App" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Starting the application..." -ForegroundColor Green
Write-Host ""
Write-Host "Open your browser and go to: " -NoNewline -ForegroundColor White
Write-Host "http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "d:\Placement Preparation\Python Projects\Web-based-pdf Converter Practise"
& "D:/Placement Preparation/Python Projects/Web-based-pdf Converter Practise/.venv/Scripts/python.exe" app.py

Read-Host "Press Enter to continue..."
