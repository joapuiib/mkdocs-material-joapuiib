#!/bin/bash

function print {
    GREEN="\033[0;32m"
    RESET="\033[0m"
    echo -e "${GREEN}$1${RESET}"
}

BUILD=0
INSTALL_VENV=0
PROD=0
ARGS=''
while [ $# -gt 0 ] ; do
    case $1 in
        -b)
            BUILD=1
            ;;
        -p)
            PROD=1
            ;;
        --install-venv)
            INSTALL_VENV=1
            ;;
        *)
            ARGS="$ARGS $1"
            ;;
    esac
    shift
done

if [ ! -d "venv" ]; then
    INSTALL_VENV=1
    print "Virtual environment not found."
fi

if [ $INSTALL_VENV -eq 1 ]; then
    if [ -d "venv" ]; then
        print "Removing existing virtual environment..."
        rm -rf venv
    fi

    print "Installing virtual environment..."
    python3 -m venv venv
    print "Installing this package"
    ./venv/bin/pip install -e .
    print "Installing dependencies"
    ./venv/bin/pip install -r requirements.txt
fi

if [ $PROD -eq 1 ]; then
    export SHOW_PROTECTED_CONTENT=false
fi

COMMAND="serve --watch-theme"
if [ $BUILD -eq 1 ]; then
    COMMAND="build"
fi

./venv/bin/mkdocs $COMMAND $ARGS
