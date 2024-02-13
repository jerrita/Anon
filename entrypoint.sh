#!/bin/sh

if [ ! -d /app ]; then
  echo "/app not exists!"
  exit 1
fi

if [ ! -f /app/anon ]; then
  cp -r /repo/anon /app
fi

if [ -f /app/requirements.txt ] && [ ! -f /app/.installed ]; then
  pip install -r /app/requirements.txt
fi

cd /app && python main.py
