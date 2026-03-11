FROM golang:1.23-alpine AS base

RUN apk add --no-cache python3 py3-pip curl bash gcc musl-dev

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /workspace

COPY . .

RUN cd engine && go build -o scanner .

RUN cd reporter && cargo build --release

COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]