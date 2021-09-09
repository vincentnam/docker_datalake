#!/bin/bash
BASEDIR=$(dirname "$0")

ansible-playbook -i $BASEDIR/../../../inventories/staging/hosts.yml $BASEDIR/main.yml
