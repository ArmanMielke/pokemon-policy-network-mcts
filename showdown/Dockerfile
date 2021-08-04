FROM node
RUN apt update && apt upgrade -y
RUN apt install -y git
RUN git clone https://github.com/smogon/pokemon-showdown.git
WORKDIR pokemon-showdown
RUN git checkout d4cec9736f03d177fd5216abbcb9beee95600811
COPY formats.ts config/formats.ts
RUN ./build
ENTRYPOINT ./pokemon-showdown 8081 --no-security
#ENTRYPOINT ["node","pokemon-showdown", "start", "--no-security"]
