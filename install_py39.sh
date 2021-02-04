#!/bin/bash
# Installing Python 3.9
## Installing dependencies

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

printf "Installing Dependencies\n"
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
libnss3-dev libssl-dev libreadline-dev libffi-dev wget -y &>> ../install.og
cd /tmp
printf "Downloading Python 3.9.0\n"
wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz &>> ../install.og
printf "Untaring Python 3.9.0\n"
tar -xf Python-3.9.0.tgz &> ../install.og
cd Python-3.9.0
printf "Configuring Python 3.9.0\n"
./configure --enable-optimizations &>> ../install.og
printf "Alternate Installing Python 3.9.0\n"
sudo make altinstall &>> ../install.og
cd ../
rm -rf Python-3.9.0.tgz Python-3.9.0/