#!/usr/bin/env bash

#find-corner-k3 host all-black|top-left|top-right|bottom-left|bottom-right

ssh -i kindle-rsa root@$1 "/usr/sbin/eips -g /mnt/us/perspectives/$2.png"
