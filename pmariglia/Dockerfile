FROM pmariglia/gambit-docker as debian-with-gambit

FROM python:3.6-slim

COPY --from=debian-with-gambit /usr/local/bin/gambit-enummixed /usr/local/bin
RUN apt update
RUN apt install -y git
RUN git clone https://github.com/pmariglia/showdown.git

WORKDIR /showdown

#COPY requirements.txt /showdown/requirements.txt

RUN pip3 install -r requirements.txt

#COPY config.py /showdown/config.py
#COPY constants.py /showdown/constants.py
#COPY data /showdown/data
#COPY run.py /showdown/run.py
#COPY showdown /showdown/showdown
#COPY teams /showdown/teams

COPY .env /showdown/.env

ENV PYTHONIOENCODING=utf-8
ENV GAMBIT_PATH=gambit-enummixed
EXPOSE 8081
CMD ["python3", "run.py"]
