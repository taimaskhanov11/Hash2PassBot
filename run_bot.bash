#!/usr/bin/env bash
# killall gcalctool /home/user/.cache/pypoetry/virtualenvs/hash2passbot-vOgQLhOe-py3.10/bin/python &&
pkill -f hash2passbot/main.py &&
poetry run python hash2passbot/main.py &
poetry run uvicorn api_server:app --port 8001 --app-dir=hash2passbot/apps/api && fg
