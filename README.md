# QuiCC Covert Channel Demo

## Quickstart

### Install Requirements

```bash
pip3 install aioquic/ pycryptodome dnslib jinja2 starlette wsproto
```

### Start the server

```bash
python aioquic/examples/http3_server.py --certificate aioquic/tests/ssl_cert.pem --private-key aioquic/tests/ssl_key.pem
```

### Send a file

```bash
python aioquic/examples/http3_client.py --ca-certs aioquic/tests/pycacert.pem wss://localhost:4433/ws
```