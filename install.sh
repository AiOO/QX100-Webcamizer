#!/bin/bash
git submodule update --init --recursive

pushd pyvirtualcam
pip install .
popd

pip install -r requirements.txt
