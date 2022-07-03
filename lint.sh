#!/bin/bash
black -l 79 -S run.py qx100
isort -l 79 -m 3 -p qx100 -o pyvirtualcam --tc run.py qx100
