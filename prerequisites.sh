#!/bin/bash

apt-get update
apt-get upgrade

apt-get remove bluetooth blueman bluez libbluetooth-dev
apt-get install python3

python3 -m pip install pybluez

sudo sed -i '/^ExecStart/{/-C/!{s/.*/& -C/}}' /etc/systemd/system/dbus-org.bluez.service
sudo sdptool add SP

systemctl daemon-reload
service bluetooth restart
