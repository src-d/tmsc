FROM ubuntu:16.04

RUN apt update && apt install python3 && \
    wget -O - https://bootstrap.pypa.io/get-pip.py | python3 && \
    pip3 install tmsc

CMD tmsc
