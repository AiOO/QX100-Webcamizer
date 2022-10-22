#!/bin/bash
git clone git@github.com:letmaik/pyvirtualcam.git

pushd pyvirtualcam
git submodule update --init --recursive
pip install .
popd

pip install -r requirements.txt
