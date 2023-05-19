# Check if nvm is installed
if ((Get-Command "nvm" -ErrorAction SilentlyContinue) -eq $null) {
    # Download and install nvm
    Write-Output "Installing nvm..."
    Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/coreybutler/nvm-windows/master/powershell_scripts/install.ps1' -OutFile 'install-nvm.ps1'
    if (Test-Path -Path 'install-nvm.ps1') {
        .\install-nvm.ps1
        Remove-Item .\install-nvm.ps1
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')
    } else {
        Write-Output "Failed to download nvm installer."
    }
} else {
    Write-Output "nvm is already installed."
}

# Install the latest version of Node.js
Write-Output "Installing Node.js..."
& 'nvm' 'install' 'latest'
