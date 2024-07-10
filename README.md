# QuiCC Covert Channel Demo

## Video Demonstration

Below is a video demonstration of the covert channel and an overview of the code
as it is available on this date and time.

[![Watch the video](https://img.youtube.com/vi/zcUX_P7fthk/default.jpg)](https://youtu.be/nTQUwghvy5Q)

## Quickstart

### Clone the repository and initialize submodules

```bash
git clone --recurse-submodules https://github.com/nuvious/QuiCC.git
cd QuiCC
```

### Generate RSA keys for the covert channel

```bash
openssl genpkey -algorithm RSA -out server_key.pem -pkeyopt rsa_keygen_bits:4096
openssl genpkey -algorithm RSA -out client_key.pem -pkeyopt rsa_keygen_bits:4096
openssl rsa -in client_key.pem -pubout -out client_public_key.pem
openssl rsa -in server_key.pem -pubout -out server_public_key.pem
```

### Install Requirements

For the HTTP server and client examples provided by the aioquic library, the
requirements are not included in the package dependencies so we have to install
them manually.

```bash
pip3 install aioquic/ dnslib jinja2 starlette wsproto
```

### Start the server

```bash
python http3_cc_server.py \
    --certificate aioquic/tests/ssl_cert.pem \
    --private-key aioquic/tests/ssl_key.pem \
    --cc-private-key server_key.pem
```

## Send a message

```bash
python http3_cc_client.py \
    --ca-certs aioquic/tests/pycacert.pem \
    --message "QuiCC can never be detected!" \
    --cid-size 8 \
    --cc-private-key client_key.pem \
    --cc-server-public-key server_public_key.pem \
     wss://localhost:4433/ws
```

### Send a file

```bash
python http3_cc_client.py \
    --ca-certs aioquic/tests/pycacert.pem \
    --file README.md \
    --cid-size 8 \
    --cc-private-key client_key.pem \
    --cc-server-public-key server_public_key.pem \
    wss://localhost:4433/ws
```
