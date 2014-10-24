#!/bin/bash
echo "local0.*		  /var/log/postgresql" | sudo tee -a /etc/rsyslog.conf

#LUKS,install if nessecary 
sudo yum install cryptsetup -y

sudo yum install postgresql94-server postgresql94-contrib -y

DATA_DRIVE=/dev/sdb
PW="maven"
echo $PW | sudo cryptsetup --verbose --batch-mode --key-file - luksFormat $DATA_DRIVE
echo $PW | sudo cryptsetup --key-file - luksOpen $DATA_DRIVE maven_LUKS
#Format the partition
sudo mkfs.ext4 /dev/mapper/maven_LUKS

# mount encrypted partition and initialize the database
#switch to root user
sudo su
mount -t ext4 /dev/mapper/maven_LUKS ~postgres
cd ~postgres
chown postgres ~postgres
chgrp postgres ~postgres
setenforce 0
echo 'PATH=/usr/pgsql-9.4/bin:${PATH}' >> .bashrc
su postgres
echo maven > pw
initdb -D `pwd`/9.4/data -A password --pwfile=pw
cd 9.4/data
sed -i.bak\
    -e "s/#listen_addresses = 'localhost'/listen_addresses = '\*'/" \
    -e 's/max_connections = 100/max_connections = 200/' \
    -e "s/log_destination = 'stderr'/log_destination = 'syslog'/" \
    -e "s/#syslog_/syslog_/" \
postgresql.conf

sed -i -e 's/\(local.*\)password/\1trust/' pg_hba.conf
echo "host   all    postgres          10.240.0.0/16   password
host   maven  maven             10.240.0.0/16   password" >> pg_hba.conf

exit # exit postgres
sudo usermod -G `whoami` -a postgres

sudo systemctl start postgresql-9.4
exit # exit root
echo 'PATH=/usr/pgsql-9.4/bin:${PATH}' >> ~/.bashrc

#Note - on google, EBS storage of a truecrypt encrypted partition passed the closest I can get to a "disk pull plug" test.  A single pass doesn't prove much - only that the system isn't horribly broken.  It was also getting around 120 writes/second (compared to amazon's 80).  The writes/second matches what happened without truecrypt, so I don't think encryption costs us anything.

echo '#!/bin/bash
sudo systemctl restart postgresql-9.4 '| sudo tee /etc/limited/restartpostgres
echo '#!/bin/bash
echo $1 | cryptsetup --key-file - luksOpen /dev/sdb maven_LUKS
mount -t ext4 /dev/mapper/maven_LUKS ~postgres' | sudo tee /etc/limited/mount
sudo chmod a+rx /etc/limited/restartpostgres /etc/limited/mount

echo "
/etc/limited/mount maven
/etc/limited/restartpostgres
"  | sudo tee -a /etc/rc.local

cd ~/database
sudo ./installAsRoot.sh