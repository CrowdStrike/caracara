#!/bin/bash
# Runs pylint against the source code, examples and all unit tests
poetry run pylint caracara
poetry run pylint examples
poetry run pylint tests
