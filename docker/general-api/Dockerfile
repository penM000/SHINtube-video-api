FROM python:3.9
ENV TZ=Asia/Tokyo 

RUN apt-get update &&\
    apt install -y curl ffmpeg i965-va-driver-shaders intel-media-va-driver-non-free &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*

RUN apt-get update &&\
    apt install -y curl python3-pip  &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*

RUN pip3 install -U fastapi uvicorn[standard] aiohttp aiofiles python-multipart aiopath
WORKDIR /
CMD /bin/bash
