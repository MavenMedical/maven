if [ "0" -eq `lsof|grep runme|wc -l` ]; then
  echo "Don't call me directly. Only call from runme.sh"
  exit
fi


chown postgres.postgres /var/lib/pgsql/9.3/data/*
chown postgres.postgres /var/lib/pgsql/9.3/data/*/*
chown postgres.postgres /var/lib/pgsql/9.3/data/*/*/*
service postgresql-9.3 start

