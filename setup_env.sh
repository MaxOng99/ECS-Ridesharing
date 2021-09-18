#!/bin/bash

mkdir env
python3 -m venv ./env/ride_sharing
source env/ride_sharing/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
