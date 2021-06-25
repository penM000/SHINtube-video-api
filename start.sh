#!/bin/bash
# スクリプトの場所に移動
cd `dirname $0`
pip3 install -U fastapi uvicorn aiohttp aiofiles python-multipart
if [ "root" = `whoami` ]; then
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers
else
  ~/.local/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers
fi
