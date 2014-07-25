service postgresql-9.3 stop
yum -y remove postgresql93 postgresql93-server
rm -rf /var/lib/pgsql
