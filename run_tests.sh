#!/bin/bash

set -e

python -m unittest discover pyrs
flake8 pyrs
