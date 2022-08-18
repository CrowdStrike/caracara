#!/bin/bash

ROOT="caracara"

if [ -z $1 ]
then
    TARGET=$ROOT
else
    TARGET="tests/unit_tests/test_$1.py"
fi
poetry run coverage run -m pytest -s -v $TARGET
poetry run coverage report --omit=tests/*
