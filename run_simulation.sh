#!/bin/bash

source env/ride_sharing/bin/activate

if [ -d "./temp" ]
then
    rm -r ./temp
fi

mkdir ./temp
python3 src/create_temp_files.py

for config in ./temp/*; do
    python3 src/run_single_simulation.py $config &
done

wait $(jobs -rp)


rm -r ./temp

deactivate
