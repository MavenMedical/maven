
perl -pi -e 's/#wal_level = minimal/wal_level=hot_standby/' /var/lib/pgsql/9.3/data/postgresql.conf
perl -pi -e 's/#max_wal_senders = 0/max_wal_senders = 5/' /var/lib/pgsql/9.3/data/postgresql.conf
perl -pi -e 's/#wal_keep_segments = 0/wal_keep_segments = 32/' /var/lib/pgsql/9.3/data/postgresql.conf

#echo "standby_mode = 'off'">>/var/lib/pgsql/9.3/data/recovery.conf
#echo "primary_conninfo = 'host=$1 port=5432 user=postgres'">>/var/lib/pgsql/9.3/data/recovery.conf
#echo "trigger_file = '/tmp/pgsql.trigger'">>/var/lib/pgsql/9.3/data/recovery.conf

service postgresql-9.3 start
#install maven
cd ../../../app/schema
./installAsRoot.sh
./terminology/installAsRoot.sh
./terminology/rxnorm/installAsRoot.sh
./terminology/loinc/installAsRoot.sh


