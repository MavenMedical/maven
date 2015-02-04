#!/bin/bash

cd ~postgres
su postgres -c "echo 'PATH=/usr/pgsql-9.4/bin:${PATH}' >> ~.bashrc"
su postgres -c "echo maven > pw"
su postgres -c "/usr/pgsql-9.4/bin/initdb -D `pwd`/9.4/data -A trust"
cd 9.4/data
sed -i.bak\
    -e "s/#listen_addresses = 'localhost'/listen_addresses = '\*'/" \
    -e 's/max_connections = 100/max_connections = 200/' \
    -e "s/log_destination = 'stderr'/log_destination = 'syslog'/" \
    -e "s/#syslog_/syslog_/" \
postgresql.conf

# sed -i -e 's/\(local.*\)password/\1trust/' pg_hba.conf
echo "host   all    postgres          10.240.0.0/16   password
host   maven  maven             10.240.0.0/16   password" >> pg_hba.conf
