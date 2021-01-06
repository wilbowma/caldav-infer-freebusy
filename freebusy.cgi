#!/bin/sh

echo 'Content-type: text/calendar; charset="utf-8"'
echo ""

python main.py --url http://localhost:5232 --ahead 7 --user user
