#!/bin/bash
black -l 79 -S run.py
isort -l 79 -m 3 --tc run.py
