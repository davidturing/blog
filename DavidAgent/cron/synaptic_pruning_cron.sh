#!/bin/bash
# DavidAgent 突触修剪定时任务
# 每天凌晨 3 点执行

cd /Users/zhaoqinhuang/david_project/DavidAgent
source venv/bin/activate
python3 synaptic_pruning.py >> logs/synaptic_pruning.log 2>&1