yum -y install postgresql93 postgresql93-server
service postgresql-9.3 initdb
echo "host    all     postgres        $1/32         trust">/var/lib/pgsql/9.3/data/pg_hba.conf
echo "host    all     postgres        $2/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "host    replication     postgres        $1/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "host    replication     postgres        $2/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "local all postgres trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "listen_addresses='$1,$2'">>/var/lib/pgsql/9.3/data/postgresql.conf
