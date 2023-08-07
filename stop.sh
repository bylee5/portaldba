#!/bin/bash

# 확인
ps -ef | grep "manage.py runserver"
sleep 1

# PID KILL
kill -9 `ps -ef | grep "manage.py runserver" | grep "0.0.0.0:8000" | awk '{print $2}'`
sleep 1

# 확인
ps -ef | grep "manage.py runserver"
