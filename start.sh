#!/bin/bash
# スクリプトの場所に移動
cd `dirname $0`

if [ "root" = `whoami` ]; then
  uvicorn app.main:app  --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers --reload --reload-dir ./app
else
  ~/.local/bin/uvicorn app.main:app  --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers  --reload --reload-dir ./app
fi
