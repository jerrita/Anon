#!/bin/sh

if [ ! -d /app ]; then
  echo "/app not exists!"
  exit 1
fi

if [ ! -d /app/anon ]; then
  echo "/app/anon is not dir, copying..."
  rm -rf /app/anon
  cp -r /repo/anon /app
  cp -r /repo/plugins/* /app/plugins
fi

if [ -f /app/requirements.txt ] && [ ! -f /app/.installed ]; then
  uv pip install -r /app/requirements.txt
fi

cd /app && python main.py
