#!/bin/bash

cd /var/services/homes/administer/Daily-News-Update/Script
python3 main.py >> log.txt 2>&1


cd /var/services/homes/administer/Daily-News-Update
git add .
git commit -m "Auto update $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main >> gitpush.log 2>&1


