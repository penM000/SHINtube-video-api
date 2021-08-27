#!/bin/bash
# スクリプトの場所に移動
cd `dirname $0`
sudo dpkg --configure -a || dpkg --configure -a
sudo apt update || apt update
sudo apt install ffmpeg -y || apt install ffmpeg -y
sudo dpkg --configure -a || dpkg --configure -a
pip3 install -U fastapi uvicorn aiohttp aiofiles python-multipart aiopath
if [ "root" = `whoami` ]; then
  uvicorn app.main:app  --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers --reload
else
  ~/.local/bin/uvicorn app.main:app  --host 0.0.0.0 --port 8000 --log-level debug --proxy-headers  --reload
fi
