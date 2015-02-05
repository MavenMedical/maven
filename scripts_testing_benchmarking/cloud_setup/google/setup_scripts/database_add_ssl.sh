#!/bin/bash

cd ~postgres
cd 9.4/data

cp /tmp/db-* .
chown postgres:postgres db-*
chmod 400 db-*

sed -i.bak\
 -e 's/#ssl = .*/ssl = on/' \
 -e "s/#ssl_ciphers.*/ssl_ciphers = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256'/" \
 -e "s/#ssl_ca_file.*/ssl_ca_file = 'db-cacert.crt'/" \
 -e "s/#ssl_cert_file.*/ssl_cert_file = 'db-server.crt'/" \
 -e "s/#ssl_key_file.*/ssl_key_file = 'db-server.key'/" \
postgresql.conf

echo "developer mavenmedical.net postgres
developer mavenmedical.net maven" >> pg_ident.conf

# need to put unencrypted server key (chmod 600) into data/server.key, also need server.crt and cacert.pem
# an encrypted key can be unencrypted by openssl rsa -in keyfile -out server.key
