# Start the Python server script in the background
Write-Host "Starting Python server..."
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "highlevel.py"

# Change directory to backend
Write-Host "Navigating to the backend directory..."
Start-Process -NoNewWindow -FilePath "cmd.exe" -ArgumentList "/c cd stock-analysis-react && npm start"

Write-Host "All processes started successfully."
