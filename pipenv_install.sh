#!/bin/bash

while read -r requirement; do
    echo "INSTALLING $requirement"
    pipenv run pip install $requirement
done < requirements.txt