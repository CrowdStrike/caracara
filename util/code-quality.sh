#!/bin/bash
# Run all Caracara code quality tooling

# Example result: /a/b/c/util/code-quality.sh
script_name=$0

# Example result: /a/b/c/util
script_full_path=$(dirname "$0")

# Example result: util
local_script_path=${script_full_path##*/}

# Example result: /a/b/c
root_path=$(dirname "$script_full_path")

pushd "$root_path"

# Running linters
echo Bandit
echo "******"
$local_script_path/bandit.sh

echo Pylint
echo "******"
$local_script_path/pylint.sh

popd

pushd "$root_path"

echo Flake8
echo "******"
poetry run flake8 --show-source --statistics

echo Pydocstyle
echo "**********"
poetry run pydocstyle caracara

echo "Unit Tests and Coverage"
echo "***********************"
poetry run coverage run -m pytest -s -v tests/unit_tests/test_*.py
poetry run coverage report --omit=tests/*

popd
