#!/bin/bash

EXAMPLES="examples"
ROOT="caracara"
TESTS="tests"

poetry run coverage run -m pytest -s -v
poetry run coverage report --omit=tests/*
poetry run pylint $EXAMPLES
poetry run pylint $ROOT
poetry run pylint $TESTS
poetry run flake8
poetry run bandit -r $EXAMPLES --configfile $EXAMPLES/.bandit
poetry run bandit -r $ROOT --configfile .bandit
poetry run bandit -r $TESTS --configfile $TESTS/.bandit
