FROM ubuntu:21.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt upgrade -y
RUN apt install -y curl build-essential git cmake libboost-all-dev
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
COPY . /mcts
WORKDIR /mcts
RUN mkdir build
RUN cmake -S . -B build  
RUN cmake --build build
ENTRYPOINT ./build/pokemon_mcts 
