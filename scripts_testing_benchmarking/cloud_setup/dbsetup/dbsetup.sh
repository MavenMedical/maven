#BOTH
yum -y install postgresql93 postgresql93-server
service postgresql-9.3 initdb
echo "host    all     postgres        192.168.1.19/32         trust">/var/lib/pgsql/9.3/data/pg_hba.conf
echo "host    all     postgres        192.168.1.9/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "host    replication     postgres        192.168.1.19/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "host    replication     postgres        192.168.1.9/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "local all postgres trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
echo "listen_addresses='192.168.1.9,192.168.1.19'">>/var/lib/pgsql/9.3/data/postgresql.conf

ssh 192.168.1.9 yum -y install postgresql93 postgresql93-server
ssh 192.168.1.9 service postgresql-9.3 initdb
ssh 192.168.1.9 echo "host    all     postgres        192.168.1.19/32         trust">/var/lib/pgsql/9.3/data/pg_hba.conf
ssh 192.168.1.9 echo "host    all     postgres        192.168.1.9/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
ssh 192.168.1.9 echo "host    replication     postgres        192.168.1.19/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
ssh 192.168.1.9 echo "host    replication     postgres        192.168.1.9/32         trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
ssh 192.168.1.9 echo "local all postgres trust">>/var/lib/pgsql/9.3/data/pg_hba.conf
ssh 192.168.1.9 echo "listen_addresses='192.168.1.9,192.168.1.19'">>/var/lib/pgsql/9.3/data/postgresql.conf

#MASTER
perl -pi -e 's/#wal_level = minimal/wal_level=hot_standby/' /var/lib/pgsql/9.3/data/postgresql.conf
perl -pi -e 's/#max_wal_senders = 0/max_wal_senders = 5/' /var/lib/pgsql/9.3/data/postgresql.conf
perl -pi -e 's/#wal_keep_segments = 0/wal_keep_segments = 32/' /var/lib/pgsql/9.3/data/postgresql.conf

#SLAVE
ssh 192.168.1.9 echo "hot_standby=on">>/var/lib/pgsql/9.3/data/postgresql.conf
ssh 192.168.1.9 echo "standby_mode = 'on'">>/var/lib/pgsql/9.3/data/recovery.conf
ssh 192.168.1.9 echo "primary_conninfo = 'host=192.168.1.19 port=5432 user=postgres'">>/var/lib/pgsql/9.3/data/recovery.conf
ssh 192.168.1.9 echo "trigger_file = '/tmp/pgsql.trigger'">>/var/lib/pgsql/9.3/data/recovery.conf

#MASTER
service postgresql-9.3 start
#Install Maven Database
psql -U postgres -c "create database maven; create table test(i int);"
#REMOVE ABOVE LINE
service postgresql-9.3 stop
scp -r /var/lib/pgsql/9.3/data/base/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/global/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_clog/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_log/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_multixact/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_notify/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_serial/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_snapshots/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_stat/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_stat_tmp/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_subtrans/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_tblspc/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_twophase/ 192.168.1.9:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_xlog/ 192.168.1.9:/var/lib/pgsql/9.3/data/

#STANDBY
ssh 192.168.1.9 chown postgres.postgres /var/lib/pgsql/9.3/data/*
ssh 192.168.1.9 chown postgres.postgres /var/lib/pgsql/9.3/data/*/*
ssh 192.168.1.9 chown postgres.postgres /var/lib/pgsql/9.3/data/*/*/*
ssh 192.168.1.9 service postgresql-9.3 start
