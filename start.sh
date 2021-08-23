#!/bin/bash
# スクリプトの場所に移動
cd `dirname $0`
sudo apt update || apt update
sudo apt install ffmpeg -y || apt install ffmpeg -y
pip3 install -U fastapi uvicorn aiohttp aiofiles python-multipart aiopath
if [ "root" = `whoami` ]; then
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers
else
  ~/.local/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers
fi
