#!/bin/bash
apt update
apt install -y tor
service tor status
service tor start
apt install -y netcat
echo -e 'AUTHENTICATE' | nc 127.0.0.1 9051
service tor stop
kill $(pidof tor)
service tor status
echo "ControlPort 9051" >> /etc/tor/torrc
service tor start
 echo -e 'AUTHENTICATE' | nc 127.0.0.1 9051
service tor stop
kill $(pidof tor)
echo HashedControlPassword $(tor --hash-password "my password" | tail -n 1) >> /etc/tor/torrc
tail -n 2 /etc/tor/torrc
service tor start
echo -e 'AUTHENTICATE' | nc 127.0.0.1 9051
echo -e 'AUTHENTICATE "my password"' | nc 127.0.0.1 9051
apt install -y curl

apt install -y python3.8 python3-pip
pip3 install pipenv
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
pipenv install
pipenv shell