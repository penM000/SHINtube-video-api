FROM nvidia/cuda:11.4.1-devel-ubuntu20.04
RUN apt-get update &&\
    apt-get -y install build-essential yasm cmake libtool libc6 libc6-dev unzip wget libnuma1 libnuma-dev git
WORKDIR /WORKDIR

RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git &&\
    cd nv-codec-headers && \
    sudo make install 
RUN git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg/
    cd ffmpeg && \
    ./configure --enable-nonfree --enable-cuda-nvcc –enable-libnpp --extra-cflags=-I/usr/local/cuda/include --extra-ldflags=-L/usr/local/cuda/lib64 --nvccflags="-gencode arch=compute_52,code=sm_52 -O2" && \
    make -j$(nproc)
    make install