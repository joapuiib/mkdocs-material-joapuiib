#!/bin/bash

function print {
    GREEN="\033[0;32m"
    RESET="\033[0m"
    echo -e "${GREEN}$1${RESET}"
}

BUILD=0
INSTALL_VENV=0
SPELL=0
ACT=''
ALL=0
DEV=0

ARGS=''
SPELL_ARGS=''
while [ $# -gt 0 ] ; do
    case $1 in
        -b)
            BUILD=1
            ;;
        -d)
            DEV=1
            ;;
        --install-venv)
            INSTALL_VENV=1
            ;;
        --spell)
            BUILD=1
            SPELL=1
            ARGS="$ARGS --clean"
            ;;
        --all)
            ALL=1
            ;;
        --act)
            ACT=$2
            if [ -z "$ACT" ]; then
                print "Missing workflow name."
                exit 1
            fi
            shift
            ;;
        *)
            ARGS="$ARGS $1"
            ;;
    esac
    shift
done

if [ -n "$ACT" ]; then
    if ! which act 2>/dev/null; then
        print "act not found."
        exit 1
    fi
    if [ ! -f ".github/workflows/$ACT" ]; then
        print "Workflow $ACT not found."
        exit 1
    fi
    act -W .github/workflows/$ACT
    exit
fi

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
    print "Installing this theme"
    ./venv/bin/pip install -e .
    print "Installing dependencies"
    ./venv/bin/pip install -r requirements.txt
fi

source venv/bin/activate
if [ $DEV -eq 1 ]; then
    export SHOW_PROTECTED_CONTENT="false";
fi

COMMAND="serve --watch-theme"
if [ $BUILD -eq 1 ]; then
    COMMAND="build"
fi

mkdocs $COMMAND $ARGS
if [ $? -ne 0 ]; then
    print "Error building site."
    exit 1
fi

if [ $SPELL -eq 1 ]; then
    export DICPATH=.hunspell/
    print "Checking spelling..."
    mkdir -p .hunspell

    if ! python -c 'import pyspelling' 2>/dev/null; then
        print "Installing pyspelling..."
        pip install pyspelling
    fi

    if [ ! -f .hunspell/ca_ES_valencia.dic ]; then
        print "Downloading ca_ES_valencia dictionary..."
        curl -L https://raw.githubusercontent.com/Softcatala/catalan-dict-tools/refs/heads/master/resultats/hunspell/catalan-valencia.dic -o .hunspell/ca_ES_valencia.dic
    fi
    if [ ! -f .hunspell/ca_ES_valencia.aff ]; then
        print "Downloading ca_ES_valencia affix file..."
        curl -L https://raw.githubusercontent.com/Softcatala/catalan-dict-tools/refs/heads/master/resultats/hunspell/catalan-valencia.aff -o .hunspell/ca_ES_valencia.aff
    fi

    SOURCES=''
    if [ $ALL -eq 0 ]; then
        CHANGED_FILES=$(git status --porcelain | grep '\.md$' | awk '{print $2}' | sed 's/docs/site/' | sed 's/.md$/\/index.html/')
        if [ -z "$CHANGED_FILES" ]; then
            print "No changes found."
            exit
        fi
        for FILE in $CHANGED_FILES; do
            if [ -f $FILE ]; then
                SOURCES="$SOURCES -S $FILE"
            fi
        done
        SPELL_ARGS="$SPELL_ARGS --name mkdocs $SOURCES"
    fi

    print "Running pyspelling..."
    echo "pyspelling $SPELL_ARGS"
    pyspelling $SPELL_ARGS | tee pyspelling.log
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        less pyspelling.log
    fi
fi
