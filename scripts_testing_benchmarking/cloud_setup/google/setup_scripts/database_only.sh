#!/bin/bash
echo "local0.*		  /var/log/postgresql" | sudo tee -a /etc/rsyslog.conf

#LUKS,install if nessecary 
sudo yum install cryptsetup -y

#Install PostgreSQL (the repos were added by common.sh)
sudo yum install postgresql94 postgresql94-server postgresql94-contrib -y

DATA_DRIVE=/dev/sdb
PW="maven"
echo $PW | sudo cryptsetup --verbose --batch-mode --key-file - luksFormat $DATA_DRIVE
echo $PW | sudo cryptsetup --key-file - luksOpen $DATA_DRIVE maven_LUKS
#Format the partition
sudo mkfs.ext4 /dev/mapper/maven_LUKS

# mount encrypted partition and initialize the database
#switch to root user
#sudo su --> this causes the script to hang, not sure what changed in the gcutil-to-gcloud transition
sudo mount -t ext4 /dev/mapper/maven_LUKS ~postgres
sudo cd ~postgres
sudo chown postgres ~postgres
sudo chgrp postgres ~postgres
sudo setenforce 0

# Run database set-up commands as the Root user
sudo su -c "bash postgres_helper.sh"

sudo usermod -G `whoami` -a postgres
sudo systemctl start postgresql-9.4
sudo systemctl enable postgresql-9.4
sudo echo 'PATH=/usr/pgsql-9.4/bin:${PATH}' >> ~/.bashrc

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

chmod g+rx /home/devel
cd ~/database
sudo ./installAsRoot.sh
cd ~/maven/scripts_testing_benchmarking/gitHooks/cloudBoxes
./explicit-db-update