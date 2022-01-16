FROM nvidia/cuda:11.4.1-devel-ubuntu20.04 

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y tzdata

ENV TZ=Asia/Tokyo 

RUN apt-get update && \
    apt-get install -y \
        git \
        pkg-config \
        curl &&\
    apt-get install -y \ 
        build-essential \
        yasm \
        cmake \
        libtool \
        libc6 \
        libc6-dev \
        unzip \
        wget \
        libnuma1 \
        libnuma-dev && \
    apt-get install -y \ 
        libgnutls28-dev \
        libaom-dev \
        libass-dev \
        libfdk-aac-dev \
        libmp3lame-dev \
        libopus-dev \
        libvorbis-dev \
        libvpx-dev \
        libx264-dev \
        libx265-dev && \
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*


WORKDIR /WORKDIR

RUN git clone https://github.com/FFmpeg/nv-codec-headers.git &&\
    cd nv-codec-headers && \
    make install && \
    cd /WORKDIR && \
    rm -r nv-codec-headers


RUN git clone https://github.com/FFmpeg/FFmpeg ffmpeg/  -b n5.0 --depth 1 &&\
    cd ffmpeg && \
    ./configure \
        --enable-nonfree \
        --enable-cuda-nvcc \
        --enable-libnpp \
        --extra-cflags=-I/usr/local/cuda/include \
        --extra-ldflags=-L/usr/local/cuda/lib64 \
        --nvccflags="-gencode arch=compute_75,code=sm_75 -O2" \
        --enable-gpl \
        --enable-gnutls \
        --enable-libaom \
        --enable-libass \
        --enable-libfdk-aac \
        --enable-libfreetype \
        --enable-libmp3lame \
        --enable-libopus \
        --enable-libvorbis \
        --enable-libvpx \
        --enable-libx264 \
        --enable-libx265 && \
    make -j$(nproc) && \
    make install && \
    cd /WORKDIR && \
    rm -r ffmpeg && \
    mkdir -p /opt/bin && \
    mv /usr/local/bin/ffmpeg /opt/bin/ffmpeg && \
    mv /usr/local/bin/ffprobe /opt/bin/ffprobe 


RUN apt-get update &&\
    apt-get -y install ffmpeg i965-va-driver-shaders intel-media-va-driver-non-free &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*

RUN apt-get update &&\
    apt-get -y install python3-pip  &&\
    apt-get clean  &&\
    rm -r /var/lib/apt/lists/*

RUN pip3 install -U fastapi uvicorn[standard] aiohttp aiofiles python-multipart aiopath


WORKDIR /
CMD /bin/bash
