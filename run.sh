#!/bin/bash

if [  ! -f $HOME/.profile_config ]; then
   cd /var/userbootstrap
   printf -- "--------------------------------------------------------------\n"
   printf "Starting user configuration script. This could take some time.\n"
   printf -- "--------------------------------------------------------------\n"
   pipenv install --ignore-pipfile &> /dev/null
   if [ $? -eq 0 ]; then
      pipenv run python bootstrap.py
   else
      printf "The pipenv environment failed to setup.\n"
      printf "You will need to setup your account manually.\n\n"
   fi
   if [ $? -eq 0 ]; then
      printf -- "----------------------------------------------------------------\n"
      printf "Your account is setup correctly.\nPlease logout to finish setup.\n"
      printf "(You can use the logout command)\n\n"
      printf -- "----------------------------------------------------------------\n"
      touch $HOME/.profile_config
   else
      printf -- "--------------------------------------\n"
      printf "The setup script encountered an error.\n"
      printf "I'll try again next time you login.\n"
      printf -- "--------------------------------------\n"
   fi
   printf "Cleaning up\n"
   pipenv --rm &> /dev/null
fi
