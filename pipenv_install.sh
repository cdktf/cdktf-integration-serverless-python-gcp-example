#!/bin/bash

while read -r requirement; do
    echo "INSTALLING $requirement"
    pipenv run pipx install $requirement
done < requirements.txt