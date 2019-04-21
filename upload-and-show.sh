#!/usr/bin/env bash

PATH_ON_KINDLE="/mnt/us/$2"
scp -i /home/pi/stand/kindle-rsa $2 root@$1:$PATH_ON_KINDLE
#ssh -i kindle-rsa root@$1 "/usr/sbin/eips -c"
ssh -i /home/pi/stand/kindle-rsa root@$1 "/usr/sbin/eips -d l=0,w=600,h=800; /usr/sbin/eips -c; /usr/sbin/eips -g $PATH_ON_KINDLE"
#ssh -i kindle-rsa root@$1 "/usr/sbin/eips -g $PATH_ON_KINDLE"
