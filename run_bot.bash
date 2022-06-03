#!/usr/bin/env bash
killall gcalctool /home/user/.cache/pypoetry/virtualenvs/hash2passbot-vOgQLhOe-py3.10/bin/python &&
poetry run uvicorn api_server:app --port 8001 --app-dir=hash2passbot/apps/api &
poetry run python hash2passbot/main.py && fg
