#!/bin/sh

set -e

python -m pip install -e . --break-system-packages

echo "Installing the Standard Library..."

PREFIX="/usr/local"

sudo install -Dm755 ouroboros "$PREFIX/bin/ouroboros"

sudo mkdir -p "$PREFIX/include/ouroboros"

sudo cp std/*.hpp "$PREFIX/include/ouroboros/"

echo "Installed Ouroboros Successfully!"