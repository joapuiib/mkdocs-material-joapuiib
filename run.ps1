function Print-GreenText {
    param (
        [string]$Message
    )
    $green = "32"
    $reset = "0"
    Write-Host "$([char]27)[0;${green}m$Message$([char]27)[${reset}m"
}

$BUILD = $false
$INSTALL_VENV = $false
$COMMAND_ARGS = @()  # Initialize $COMMAND_ARGS as an empty array

foreach ($arg in $args) {
    switch ($arg) {
        '-b' { $BUILD = $true }
        '--build' { $BUILD = $true }
        '--install-venv' { $INSTALL_VENV = $true }
        default { $COMMAND_ARGS += $arg }  # Append the argument to the array
    }
}

# Check if the virtual environment folder exists
if (-not (Test-Path -Path "venv")) {
    $INSTALL_VENV = $true
    Print-GreenText "Virtual environment not found."
}

# Install virtual environment if needed
if ($INSTALL_VENV) {
    if (Test-Path -Path "venv") {
        Print-GreenText "Removing existing virtual environment..."
        Remove-Item -Recurse -Force "venv"
    }

    Print-GreenText "Installing virtual environment..."
    python -m venv venv

    Print-GreenText "Installing this package"
    & "./venv/Scripts/pip" install -e .

    Print-GreenText "Installing dependencies"
    & "./venv/Scripts/pip" install -r requirements.txt
}

# Determine the command to run
$COMMAND = "serve"
if ($BUILD) {
    $COMMAND = "build"
}

# print args
Print-GreenText "./venv/Scripts/mkdocs $COMMAND $COMMAND_ARGS"

# Run the mkdocs command with any additional arguments
./venv/Scripts/mkdocs $COMMAND $COMMAND_ARGS