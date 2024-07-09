# QuiCC Covert Channel Demo

## Quickstart

### Generate RSA keys for the covert channel

```bash
openssl genpkey -algorithm RSA -out server_key.pem -pkeyopt rsa_keygen_bits:4096
openssl genpkey -algorithm RSA -out client_key.pem -pkeyopt rsa_keygen_bits:4096
openssl rsa -in server_key.pem -pubout -out server_public_key.pem
```

### Install Requirements

```bash
pip3 install aioquic/ pycryptodome dnslib jinja2 starlette wsproto
```

### Start the server

```bash
python aioquic/examples/http3_server.py \
    --certificate aioquic/tests/ssl_cert.pem \
    --private-key aioquic/tests/ssl_key.pem
```

### Send a file

```bash
python http3_cc_client.py \
    --ca-certs aioquic/tests/pycacert.pem \
    --file README.md \
    --cid-size 14 \
    --cc-private-key client_key.pem \
    --cc-server-public-key server_public_key.pem \
    wss://localhost:4433/ws
```
