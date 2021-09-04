FROM nvidia/cuda:11.4.1-devel-ubuntu20.04 

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y tzdata

ENV TZ=Asia/Tokyo 

RUN apt-get update &&\
    apt-get -y install build-essential yasm cmake libtool libc6 libc6-dev unzip wget libnuma1 libnuma-dev git pkg-config curl python3-pip ffmpeg &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*


RUN pip3 install -U fastapi uvicorn[standard] aiohttp aiofiles python-multipart aiopath

WORKDIR /WORKDIR

RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git &&\
    cd nv-codec-headers && \
    make install && \
    cd /WORKDIR && \
    rm -r nv-codec-headers

RUN git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg/ &&\
    cd ffmpeg && \
    ./configure \
        --enable-nonfree \
        --enable-cuda-nvcc \
        --enable-libnpp \
        --extra-cflags=-I/usr/local/cuda/include \
        --extra-ldflags=-L/usr/local/cuda/lib64 \
        --nvccflags="-arch=sm_75" \
        --nvccflags="-gencode arch=compute_75,code=sm_75 -O2" \
        --nvccflags="-gencode arch=compute_80,code=sm_80 -O2" \
        --nvccflags="-gencode arch=compute_86,code=sm_86 -O2" \
        --nvccflags="-gencode arch=compute_86,code=compute_86 -O2" \
        --nvccflags="-gencode arch=compute_87,code=sm_87 -O2" &&\
    make -j$(nproc) && \
    make install && \
    cd /WORKDIR && \
    rm -r ffmpeg && \
    mkdir -p /opt/bin && \
    mv /usr/local/bin/ffmpeg /opt/bin/ffmpeg && \
    mv /usr/local/bin/ffprobe /opt/bin/ffprobe 

WORKDIR /
CMD /bin/bash
