#!/bin/bash
# Installs Poetry and the dependencies

# Upgrade pip to the latest version
python -m pip install --upgrade pip

# Installs the Preview version of Poetry
# The Preview version will not be needed once Poetry v2 is made final
python -m pip install poetry --pre

# Installs all dependencies
poetry install
