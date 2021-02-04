#!/bin/bash

cd /var/userbootstrap
pipenv install
if [ $? -eq 0 ]; then
   pipenv run python bootstrap.py
else
   printf "The pipenv environment failed to setup.\n"
   printf "You will need to setup your account manually.\n\n"
fi
pipenv --rm

printf "Your account is setup correctly.\nPlease logout to finish setup.\n"
printf "(You can use the `logout` command)\n\n"
