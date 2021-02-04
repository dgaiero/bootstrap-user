#!/bin/bash

if [ -e $HOME/.profile ]  
then 
   cd /var/userbootstrap
   printf "Starting user configuration script. This could take some time.\n"
   pipenv install --ignore-pipfile &> /dev/null
   if [ $? -eq 0 ]; then
      pipenv run python bootstrap.py
   else
      printf "The pipenv environment failed to setup.\n"
      printf "You will need to setup your account manually.\n\n"
   fi
   printf "Cleaning up\n"
   pipenv --rm &> /dev/null

   printf "Your account is setup correctly.\nPlease logout to finish setup.\n"
   printf "(You can use the logout command)\n\n"
else  
    touch $HOME/.profile
fi
