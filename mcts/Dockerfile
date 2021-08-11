FROM nvidia/cuda:11.4.1-cudnn8-devel-ubuntu20.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt upgrade -y
RUN apt install -y wget curl gpg apt-transport-https
RUN wget https://apt.kitware.com/kitware-archive.sh
RUN chmod +x kitware-archive.sh && ./kitware-archive.sh
RUN apt install -y unzip cmake build-essential git libboost-all-dev
RUN curl -sL https://deb.nodesource.com/setup_16.x | bash - 
RUN apt update && apt install -y nodejs
RUN git clone --recursive https://github.com/nlohmann/json.git /json
RUN mkdir /json_build
RUN cmake -S /json -B /json_build
RUN cmake --build /json_build --target install --config Release
RUN git clone --recursive https://github.com/derkaczda/pokemon-showdown.git /showdown
WORKDIR /showdown
RUN ./build
WORKDIR /
RUN wget https://download.pytorch.org/libtorch/nightly/cpu/libtorch-shared-with-deps-latest.zip
RUN unzip libtorch-shared-with-deps-latest.zip
COPY . /mcts
WORKDIR /mcts
RUN mkdir build
RUN cmake -S . -B build -DCMAKE_PREFIX_PATH=/libtorch
RUN cmake --build build
ENTRYPOINT ./build/pokemon_mcts 
