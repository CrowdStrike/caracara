#!/bin/bash
awk '/\[tool.poetry.scripts\]/ { extract=1 ; next } extract { if ( NF == 0) { exit } ; if ( $1 != "#" ) { print $1 }}' pyproject.toml
