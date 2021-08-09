FROM ubuntu
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt upgrade -y
RUN apt install -y build-essential git cmake libboost-all-dev
RUN git clone --recursive https://github.com/nlohmann/json.git
RUN mkdir json_build
RUN cmake -S json -B json_build
RUN cmake --build json_build --target install --config Release
COPY . mcts
WORKDIR mcts
RUN mkdir build
RUN cmake -S . -B build  
RUN cmake --build build
ENTRYPOINT ./build/pokemon_mcts 
