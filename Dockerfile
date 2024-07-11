FROM python:3.9-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install openssl libssl-dev build-essential -y

SHELL ["/bin/bash", "-c"]

COPY . .

RUN openssl genpkey -algorithm RSA -out server_key.pem -pkeyopt rsa_keygen_bits:4096 && \
    openssl genpkey -algorithm RSA -out client_key.pem -pkeyopt rsa_keygen_bits:4096 && \
    openssl rsa -in client_key.pem -pubout -out client_public_key.pem && \
    openssl rsa -in server_key.pem -pubout -out server_public_key.pem && \
    openssl genrsa -out ca-key.pem 4096 && \
    openssl req -new -x509 -days 365 -key ca-key.pem -out aioquic/tests/pycacert.pem -subj '/CN=QuiCCA' && \
    openssl genrsa -out aioquic/tests/ssl_key.pem 4096 && \
    openssl req -new -key aioquic/tests/ssl_key.pem -out csr.pem -subj '/CN=quicc' -nodes && \
    openssl x509 -req -in csr.pem -out aioquic/tests/ssl_cert.pem \
      -CA aioquic/tests/pycacert.pem -CAkey ca-key.pem -CAcreateserial -days 3650 \
      -extfile <(printf "subjectAltName=DNS:quicc\nkeyUsage=digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth,clientAuth\nbasicConstraints=CA:FALSE\nsubjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer\nauthorityInfoAccess=caIssuers;URI:http://testca.pythontest.net/testca/pycacert.cer,OCSP;URI:http://testca.pythontest.net/testca/ocsp/\ncrlDistributionPoints=URI:http://testca.pythontest.net/testca/revocation.crl") && \
    pip3 install aioquic/ dnslib jinja2 starlette wsproto

  SHELL [ "/bin/sh" ]