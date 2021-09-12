#!/usr/bin/env bash
# repalce <ip> with domain or ip
# can be used in multiple scenarios
# in case of production system remove --min-rate=1000
# name: m1kU
# date: 12/09/2021

ports=$(nmap -p- --min-rate=1000 -T4 -oA open_ports <ip> | grep ^[0-9] | cut -d '/' -f 1 | tr '\n' ',' | sed s/,$//)
nmap -sC -sV -p$ports -oA detailed_scan <ip>
