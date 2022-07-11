ARG PYTHON_VERSION=3.10

# builder

FROM python:${PYTHON_VERSION}-slim as builder
WORKDIR /root
COPY requirements.txt /root

RUN apt update && apt install -y python3-pip
RUN pip install --prefix="/install" --no-warn-script-location -r requirements.txt

# runtime

FROM python:${PYTHON_VERSION}-slim

WORKDIR /root

RUN mkdir waifu

WORKDIR /root/waifu

COPY ./ ./

COPY --from=builder /install /usr/local

CMD [ "python3", "./main.py" ]
