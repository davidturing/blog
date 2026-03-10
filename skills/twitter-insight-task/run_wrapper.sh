#!/bin/bash
python3 run.py "$@" > /tmp/twitter_run.log 2>&1
echo "Exit code: $?" >> /tmp/twitter_run.log
