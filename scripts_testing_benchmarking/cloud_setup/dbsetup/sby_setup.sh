#TAKES THE MASTER IP AS A PARAM
if [ "0" -eq `lsof|grep runme|wc -l` ]; then
  echo "Don't call me directly. Only call from runme.sh"
  exit
fi


echo "hot_standby=on">>/var/lib/pgsql/9.3/data/postgresql.conf
echo "standby_mode = 'on'">>/var/lib/pgsql/9.3/data/recovery.conf
echo "primary_conninfo = 'host=$1 port=5432 user=postgres'">>/var/lib/pgsql/9.3/data/recovery.conf
echo "trigger_file = '/tmp/pgsql.trigger'">>/var/lib/pgsql/9.3/data/recovery.conf
