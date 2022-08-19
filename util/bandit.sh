#!/bin/bash
# This script executes the bandit security tool against the code within this repo
poetry run bandit -r caracara --configfile .bandit
poetry run bandit -r examples --configfile examples/.bandit
poetry run bandit -r tests --configfile tests/.bandit
