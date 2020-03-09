FROM python:3.7-alpine as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

COPY . /app

RUN pip3 install --install-option="--prefix=/install" /app

FROM base

COPY --from=builder /install /usr/local
RUN pip3 install python-dotenv

WORKDIR /

CMD ["python3", "-m", "mailping.main"]
