#!/bin/bash

MANAGE_DIR="/path/to/portaldba"

/usr/bin/python3 ${MANAGE_DIR}/manage.py runserver 0.0.0.0:8000 >> ${MANAGE_DIR}/portaldba.log 2>&1 &
