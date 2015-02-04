#!/bin/bash
if [ -e common.started ]; then
    exit 0
fi
touch common.started

sudo yum update -y
sudo yum install epel-release -y
sudo yum install elinks screen git emacs kernel-headers fuse-libs fuse-devel fuse lvm2 wireshark nc iptraf iftop psacct pam-devel collectl pcre-devel zlib-devel openssl-devel gcc libpqxx-devel libpqxx libffi-devel readline-devel -y

sudo sed -i -e 's/^create$/create 640 root adm/' /etc/logrotate.conf

sudo chgrp -R adm /var/log
sudo chmod -R g+r /var/log

cd
#for python3
wget http://www.python.org/ftp/python/3.4.2/Python-3.4.2.tar.xz
xz -d Python-3.4.2.tar.xz
tar -xvf Python-3.4.2.tar
cd Python-3.4.2
./configure
make -j 4
sudo make altinstall

wget http://yum.postgresql.org/9.4/redhat/rhel-7-x86_64/pgdg-centos94-9.4-1.noarch.rpm
sudo yum install pgdg-centos94-9.4-1.noarch.rpm -y
sudo yum install postgresql94
sudo ln -s /usr/pgsql-0.4/bin/psql /usr/bin

sudo usermod -a -G adm devel
sudo mkdir /etc/mavenmedical
sudo cp maven.config /etc/mavenmedical/
sudo chmod 755 /etc/mavenmedical /etc/mavenmedical/*
echo "/var/log/audit /var/log/messages /var/log/secure /tmp/maven" | sudo tee /etc/mavenmedical/logs

# user crontab -e to run this once (or more often) per day
#env PATH=/usr/bin:/usr/local/bin gsutil cp -R -z -n `cat /etc/mavenmedical/logs` gs://maven-medical/logs/

# next, setup default logging and configuration scripts

sudo mkdir /etc/limited
sudo chmod -R 755 /etc/limited

#%adm ALL=(postgres)NOPASSWD: /usr/bin/mount,/etc/limited/restartpostgres,/etc/limited/restartnginx 
