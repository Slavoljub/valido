# Ensure script works cross-platform
$ErrorActionPreference = "Stop"

# Configuration: Set certificate validity (in days)
$certValidityDays = 7300  # 20 years; change to 5475 for 15 years or other value as needed

# Function to install mkcert if not present
function Install-Mkcert {
    Write-Output "Checking for mkcert..."
    if (-not (Get-Command mkcert -ErrorAction SilentlyContinue)) {
        Write-Output "mkcert not found. Attempting to install..."
        if ($IsWindows -or $PSVersionTable.Platform -eq "Win32NT") {
            # Windows: Try Chocolatey
            if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
                Write-Output "Chocolatey not found. Installing Chocolatey..."
                Set-ExecutionPolicy Bypass -Scope Process -Force
                [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
                Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
            }
            Write-Output "Installing mkcert via Chocolatey..."
            choco install mkcert -y
        }
        elseif ($IsMacOS -or $PSVersionTable.Platform -eq "Unix" -and (uname -s) -eq "Darwin") {
            # macOS: Try Homebrew
            if (-not (Get-Command brew -ErrorAction SilentlyContinue)) {
                Write-Output "Homebrew not found. Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                # Add Homebrew to PATH for the current session
                $env:PATH += ":/opt/homebrew/bin:/usr/local/bin"
            }
            Write-Output "Installing mkcert via Homebrew..."
            brew install mkcert
        }
        elseif ($IsLinux -or $PSVersionTable.Platform -eq "Unix") {
            # Linux: Try Homebrew
            if (-not (Get-Command brew -ErrorAction SilentlyContinue)) {
                Write-Output "Homebrew not found. Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                # Add Homebrew to PATH for the current session
                $env:PATH += ":/home/linuxbrew/.linuxbrew/bin:/usr/local/bin"
            }
            Write-Output "Installing mkcert via Homebrew..."
            brew install mkcert
        }
        else {
            Write-Output "Unsupported platform or package manager not found."
            Write-Output "Please manually install mkcert from https://github.com/FiloSottile/mkcert and ensure it's in your PATH."
            exit 1
        }
        # Verify installation
        if (-not (Get-Command mkcert -ErrorAction SilentlyContinue)) {
            Write-Output "Failed to install mkcert. Please install it manually from https://github.com/FiloSottile/mkcert."
            exit 1
        }
        Write-Output "mkcert installed successfully."
    }
    else {
        Write-Output "mkcert is already installed."
    }
}

# Function to install OpenSSL if not present
function Install-OpenSSL {
    Write-Output "Checking for OpenSSL..."
    if (-not (Get-Command openssl -ErrorAction SilentlyContinue)) {
        Write-Output "OpenSSL not found. Attempting to install..."
        if ($IsWindows -or $PSVersionTable.Platform -eq "Win32NT") {
            # Windows: Try Chocolatey
            if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
                Write-Output "Chocolatey not found. Installing Chocolatey..."
                Set-ExecutionPolicy Bypass -Scope Process -Force
                [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
                Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
            }
            Write-Output "Installing OpenSSL via Chocolatey..."
            choco install openssl -y
        }
        elseif ($IsMacOS -or $PSVersionTable.Platform -eq "Unix" -and (uname -s) -eq "Darwin") {
            # macOS: Try Homebrew
            if (-not (Get-Command brew -ErrorAction SilentlyContinue)) {
                Write-Output "Homebrew not found. Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                # Add Homebrew to PATH for the current session
                $env:PATH += ":/opt/homebrew/bin:/usr/local/bin"
            }
            Write-Output "Installing OpenSSL via Homebrew..."
            brew install openssl
        }
        elseif ($IsLinux -or $PSVersionTable.Platform -eq "Unix") {
            # Linux: Try apt-get or yum
            if (Get-Command apt-get -ErrorAction SilentlyContinue) {
                Write-Output "Installing OpenSSL via apt-get..."
                sudo apt-get update
                sudo apt-get install -y openssl
            }
            elseif (Get-Command yum -ErrorAction SilentlyContinue) {
                Write-Output "Installing OpenSSL via yum..."
                sudo yum install -y openssl
            }
            else {
                Write-Output "No supported package manager found for OpenSSL installation."
                Write-Output "Please manually install OpenSSL and ensure it's in your PATH."
                exit 1
            }
        }
        else {
            Write-Output "Unsupported platform or package manager not found."
            Write-Output "Please manually install OpenSSL and ensure it's in your PATH."
            exit 1
        }
        # Verify installation
        if (-not (Get-Command openssl -ErrorAction SilentlyContinue)) {
            Write-Output "Failed to install OpenSSL. Please install it manually."
            exit 1
        }
        Write-Output "OpenSSL installed successfully."
    }
    else {
        Write-Output "OpenSSL is already installed."
    }
}

# Install mkcert and OpenSSL if not present
Install-Mkcert
Install-OpenSSL

# List all certificate files in the current directory that include 'localhost' in their name
$localhostCerts = Get-ChildItem -Path . -Filter "*localhost*" -File | Where-Object { $_.Extension -in @(".crt", ".pem", ".key") }
if ($localhostCerts.Count -gt 0) {
    Write-Output "Found existing certificate files with 'localhost' in their name:"
    $index = 1
    $certList = @()
    foreach ($cert in $localhostCerts) {
        $certList += [PSCustomObject]@{
            Index = $index
            Name  = $cert.Name
            Path  = $cert.FullName
            LastModified = $cert.LastWriteTime
        }
        $index++
    }
    $certList | Format-Table -Property Index, Name, LastModified -AutoSize

    # Prompt user to select certificates to remove
    Write-Output "Enter the index numbers of certificates to remove (e.g., 1, 2, 3) or 'none' to skip:"
    $userInput = Read-Host
    if ($userInput -ne "none") {
        $indicesToRemove = $userInput -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ -match '^\d+$' }
        foreach ($index in $indicesToRemove) {
            if ($index -ge 1 -and $index -le $certList.Count) {
                $certToRemove = $certList[$index - 1]
                Remove-Item -Path $certToRemove.Path -ErrorAction SilentlyContinue
                Write-Output "Removed: $($certToRemove.Name)"
            } else {
                Write-Output "Invalid index: $index"
            }
        }
    } else {
        Write-Output "No certificates removed."
    }
} else {
    Write-Output "No certificate files with 'localhost' in their name found."
}

# Generate mkcert CA for signing
Write-Output "Ensuring mkcert CA exists for signing..."
mkcert -install
$caCertPath = "$(mkcert -CAROOT)/rootCA.pem"
$caKeyPath = "$(mkcert -CAROOT)/rootCA-key.pem"
if (-not (Test-Path $caCertPath) -or -not (Test-Path $caKeyPath)) {
    Write-Output "Failed to locate mkcert CA files. Ensure mkcert is properly installed and run 'mkcert -install'."
    exit 1
}

# Generate OpenSSL configuration for localhost
$opensslConf = @"
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
x509_extensions = v3_req

[dn]
CN = localhost
O = Local Development
OU = Development
C = US

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
IP.2 = ::1
"@

# Write OpenSSL configuration to a temporary file
$confPath = "localhost.cnf"
$opensslConf | Out-File -FilePath $confPath -Encoding UTF8
Write-Output "Created OpenSSL configuration file: $confPath"

# Generate new certificate with specified validity
Write-Output "Generating new certificate for localhost (valid for $certValidityDays days)..."
openssl req -new -x509 -days $certValidityDays -key $caKeyPath -out localhost-cert.crt -config $confPath -extensions v3_req
openssl genrsa -out localhost-key.key 2048
openssl req -new -key localhost-key.key -out localhost.csr -config $confPath
openssl x509 -req -in localhost.csr -CA $caCertPath -CAkey $caKeyPath -CAcreateserial -out localhost-cert.crt -days $certValidityDays -extensions v3_req -extfile $confPath
Write-Output "New certificate generated (localhost-cert.crt, localhost-key.key, valid for $certValidityDays days)."

# Clean up temporary files
Remove-Item -Path $confPath -ErrorAction SilentlyContinue
Remove-Item -Path localhost.csr -ErrorAction SilentlyContinue
Remove-Item -Path $caCertPath.Replace("rootCA.pem", "rootCA.srl") -ErrorAction SilentlyContinue

# Install local CA to system trust store
$installOutput = mkcert -install 2>&1
if (-not ($installOutput | Select-String "The local CA is already installed")) {
    Write-Output "Installing mkcert local CA in the system trust store..."
    mkcert -install
    Write-Output "Local CA installed successfully."
} else {
    Write-Output "Local CA is already installed in the system trust store."
}