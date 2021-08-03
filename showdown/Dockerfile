FROM node
RUN apt update && apt upgrade -y
RUN apt install -y git
RUN git clone https://github.com/smogon/pokemon-showdown.git
WORKDIR pokemon-showdown
RUN git checkout ed8565a6dba3c88a35a854126855e1e9890fe404
COPY formats.ts config/formats.ts
RUN ./build
ENTRYPOINT ./pokemon-showdown 8081 --no-security
#ENTRYPOINT ["node","pokemon-showdown", "start", "--no-security"]
