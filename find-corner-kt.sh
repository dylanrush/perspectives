#!/usr/bin/env bash

#find-corner-kt.sh host all-black|top-left|top-right|bottom-left|bottom-right

if [[ $2 == 'top-left' ]]
then
  ssh -i kindle-rsa root@$1 "/usr/sbin/eips -d l=0,w=600,h=800; /usr/sbin/eips -d l=ff,w=80,h=80 -x 0 -y 0"
elif [[ $2 == 'top-right' ]]
then
  ssh -i kindle-rsa root@$1 "/usr/sbin/eips -d l=0,w=600,h=800; /usr/sbin/eips -d l=ff,w=80,h=80 -x 500 -y 0"
elif [[ $2 == 'bottom-left' ]]
then
  ssh -i kindle-rsa root@$1 "/usr/sbin/eips -d l=0,w=600,h=800; /usr/sbin/eips -d l=ff,w=80,h=80 -x 0 -y 700"
elif [[ $2 == 'bottom-right' ]]
then
  ssh -i kindle-rsa root@$1 "/usr/sbin/eips -d l=0,w=600,h=800; /usr/sbin/eips -d l=ff,w=80,h=80 -x 500 -y 700"
else
  ssh -i kindle-rsa root@$1 "/usr/sbin/eips -d l=0,w=600,h=800"
fi
