while ($true) {
    python main.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Program exited with code $($LASTEXITCODE)"
        break
    }
}