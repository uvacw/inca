#!/usr/bin/sh
apt update
apt install git python3-pip libmysqlclient-dev  -y
pip3 install virtualenv

apt install build-essential chrpath libssl-dev libxft-dev libfreetype6 libfreetype6-dev libfontconfig1 libfontconfig1-dev phantomjs -y
