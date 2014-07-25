#takes standby ip as a parameter
if [ "0" -eq `lsof|grep runme|wc -l` ]; then
  echo "Don't call me directly. Only call from runme.sh"
  exit
fi


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

