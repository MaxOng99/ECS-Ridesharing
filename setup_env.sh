#!/bin/bash

python3 -m pip install --user --upgrade pip
python3 -m pip install --user virtualenv

if [ ! -d "env" ]
then
    mkdir env
    python3 -m virtualenv ./env/ride_sharing
fi

source env/ride_sharing/bin/activate
pip install --upgrade pip
pip install -r requirements.txt