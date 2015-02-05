#!/bin/bash

cd ~postgres
su postgres -c "echo 'PATH=/usr/pgsql-9.4/bin:${PATH}' >> ~.bashrc"
su postgres -c "echo maven > pw"
su postgres -c "/usr/pgsql-9.4/bin/initdb -D `pwd`/9.4/data -A ident"
cd 9.4/data
sed -i.bak\
    -e "s/#listen_addresses = 'localhost'/listen_addresses = '\*'/" \
    -e 's/max_connections = 100/max_connections = 200/' \
    -e "s/log_destination = 'stderr'/log_destination = 'syslog'/" \
    -e "s/#syslog_/syslog_/" \
postgresql.conf

rm -f pg_hba.conf
if [ ! -r db-server.key ]; then
    echo "local all all ident
host   all    postgres          127.0.0.1/32   password
host   maven  maven             127.0.0.1/32   password
host   all    postgres          ::1/128   password
host   maven  maven             ::1/128   password
host   all    postgres          10.240.0.0/16   password
host   maven  maven             10.240.0.0/16   password" > pg_hba.conf
else
    echo "local all all ident
hostssl all postgres ::1/128 cert clientcert=1 map=developer
hostssl maven maven ::1/128 cert clientcert=1 map=developer
hostssl all postgres 127.0.0.1/32 cert clientcert=1 map=developer
hostssl maven maven 127.0.0.1/32 cert clientcert=1 map=developer
hostssl all postgres 10.240.0.0/16 cert clientcert=1 map=developer
hostssl maven maven 10.240.0.0/16 cert clientcert=1 map=developer" > pg_hba.conf
fi
chown postgres:postgres pg_hba.conf
