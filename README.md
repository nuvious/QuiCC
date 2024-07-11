# QuiCC Covert Channel Demo

## Running the demo locally

Recommend using a python virtual environment or conda.

### Clone the repository and initialize submodules

```bash
git clone --recurse-submodules https://github.com/nuvious/QuiCC.git
cd QuiCC
```

### Generate RSA keys for the covert channel

Generate RSA keys for the client and the server.

#### Server and client running on local host

```bash
openssl genpkey -algorithm RSA -out server_key.pem -pkeyopt rsa_keygen_bits:4096
openssl genpkey -algorithm RSA -out client_key.pem -pkeyopt rsa_keygen_bits:4096
openssl rsa -in client_key.pem -pubout -out client_public_key.pem
openssl rsa -in server_key.pem -pubout -out server_public_key.pem
```

#### Server and client running on separate hosts

If you're running the server on a separate machine, you'll need to change out
the example key and cert used by the server to ones that match your server
host IP. You'll need to add a entry to the dns record for the ip used; in this
case I used `quicc.local`.

On the server run the below in the root of the project:

```bash
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 365 -key ca-key.pem -out aioquic/tests/pycacert.pem -subj '/CN=QuiCCA'
openssl genrsa -out aioquic/tests/ssl_key.pem 4096
openssl req -new -key aioquic/tests/ssl_key.pem -out csr.pem -subj '/CN=quicc.local' -nodes
openssl x509 -req -in csr.pem -out aioquic/tests/ssl_cert.pem \
    -CA aioquic/tests/pycacert.pem -CAkey ca-key.pem -CAcreateserial -days 3650 \
  -extfile <(printf "subjectAltName=DNS:quicc.local\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth,clientAuth\nbasicConstraints=CA:FALSE\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\nauthorityInfoAccess=caIssuers;URI:http://testca.pythontest.net/testca/pycacert.cer,OCSP;URI:http://testca.pythontest.net/testca/ocsp/\ncrlDistributionPoints=URI:http://testca.pythontest.net/testca/revocation.crl")
```

You'll then need to copy over the `pycacert.pem` and repace the
`aioquic/tests/pycacert.pem` file with it on the client machine.

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
    --private-key aioquic/tests/ssl_key.pem
```

## Send a message

```bash
python http3_cc_client.py \
    --ca-certs aioquic/tests/pycacert.pem \
     wss://localhost:4433/ws
```

NOTE: If running the client and server on separate hosts, replace `localhost`
with the DNS entry; in this example `quicc.local`.

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

NOTE: If running the client and server on separate hosts, replace `localhost`
with the DNS entry; in this example `quicc.local`.

## Running the demo with docker-compose

```bash
docker-compose up
```

Expected output:

```bash
quicc_1   | 2024-07-11 03:59:37,717 INFO quic [6802ceaa04481025] Negotiated protocol version 0x00000001 (VERSION_1)
quicc_1   | 2024-07-11 03:59:37,727 INFO quic [6802ceaa04481025] ALPN negotiated protocol h3
quicc_1   | 2024-07-11 03:59:37,735 INFO quic RECEIVED DECRYPTED MESSAGE: b'QuiCC can never be detected!'
quicc_1   | 2024-07-11 03:59:37,736 INFO quic [6802ceaa04481025] HTTP request CONNECT /ws
quicc_1   | 2024-07-11 03:59:37,740 INFO quic [6802ceaa04481025] Connection close received (code 0x100, reason )
```
