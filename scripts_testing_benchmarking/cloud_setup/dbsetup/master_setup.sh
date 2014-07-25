#TAKES the standby IP as a parameter

perl -pi -e 's/#wal_level = minimal/wal_level=hot_standby/' /var/lib/pgsql/9.3/data/postgresql.conf
perl -pi -e 's/#max_wal_senders = 0/max_wal_senders = 5/' /var/lib/pgsql/9.3/data/postgresql.conf
perl -pi -e 's/#wal_keep_segments = 0/wal_keep_segments = 32/' /var/lib/pgsql/9.3/data/postgresql.conf

#echo "standby_mode = 'off'">>/var/lib/pgsql/9.3/data/recovery.conf
#echo "primary_conninfo = 'host=$1 port=5432 user=postgres'">>/var/lib/pgsql/9.3/data/recovery.conf
#echo "trigger_file = '/tmp/pgsql.trigger'">>/var/lib/pgsql/9.3/data/recovery.conf

service postgresql-9.3 start
#install maven
psql -U postgres -c "create table test(i int);"
#REMOVE ABOVE LINE
service postgresql-9.3 stop
scp -r /var/lib/pgsql/9.3/data/base/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/global/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_clog/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_log/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_multixact/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_notify/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_serial/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_snapshots/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_stat/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_stat_tmp/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_subtrans/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_tblspc/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_twophase/ $1:/var/lib/pgsql/9.3/data/
scp -r /var/lib/pgsql/9.3/data/pg_xlog/ $1:/var/lib/pgsql/9.3/data/
service postgresql-9.3 start

