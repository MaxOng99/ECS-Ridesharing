#!/bin/bash

system_dependencies=(
    "python3"
    "pip"
    "virtualenv"
)

echo -e "Checking system dependencies..."
system_dep_installed=true
for item in ${system_dependencies[@]}
do
    which $item > /dev/null
    if [ $? -ne 0 ]
    then
        echo -e "- $item not installed"
        $system_dep_installed=false
    else
        echo -e "- $item installed"
    fi
done

if [ "$system_dep_installed" = false ]
then
    echo "Ensure that all system dependencies are installed"
    exit 1
fi

printf "\n"
echo -e "Checking ride_sharing virtual environment..."

if [ ! -f "env/ride_sharing/bin/activate" ]
then
    echo -e "- Creating ride_sharing virtual environment..."
    mkdir env
    python3 -m virtualenv ./env/ride_sharing
else
    echo -e "- ride_sharing virtual environment already exist. Skip creation."
fi

printf "\n"
echo -e "Install project related dependencies...\n"
source env/ride_sharing/bin/activate
pip install --upgrade pip
pip install -r requirements.txt


