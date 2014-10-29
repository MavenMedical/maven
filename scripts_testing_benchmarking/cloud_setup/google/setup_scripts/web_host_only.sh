#!/bin/bash
sudo yum install pcre-devel zlib-devel openssl-devel gcc libpqxx-devel libpqxx libffi-devel policycoreutils-python-2.2.5-11.el7_0.1.x86_64 -y

echo "export MAVEN_ROOT=~/maven
export PYTHONPATH=$MAVEN_ROOT" >> .bashrc
source ~/.bashrc

cd
#for python3
wget http://www.python.org/ftp/python/3.4.1/Python-3.4.1.tar.xz
xz -d Python-3.4.1.tar.xz
tar -xvf Python-3.4.1.tar
cd Python-3.4.1
./configure
make -j 4
sudo make altinstall


cd
# python db connectivity
sudo yum install python-psycopg2 -y

cp deploy-key .ssh/id_rsa
cat github_server_fingerprint >> .ssh/known_hosts
chmod 600 .ssh/*
git clone git@github.com:MavenMedical/maven.git

cd maven
git checkout DEV
cp scripts_testing_benchmarking/gitHooks/cloudBoxes/* .git/hooks/
chmod +x .git/hooks/*

cd
# for nginx
wget http://nginx.org/packages/centos/7/noarch/RPMS/nginx-release-centos-7-0.el7.ngx.noarch.rpm
sudo rpm -i nginx-*.rpm
sudo yum install nginx -y
# sudo chkconfig nginx off

#openssl genrsa -des3 -out server.key 2048
#openssl req -new -key server.key -out server.csr
#cp server.key server.key.org
#openssl rsa -in server.key.org -out server.key
#openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
sudo cp server.crt server.key /etc/nginx/conf.d/
sudo rm /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/example_ssl.conf
sudo cp maven/scripts_testing_benchmarking/cloud_setup/nginx_dev.conf /etc/nginx/conf.d/
chmod g+rx `pwd`

sudo usermod -G `whoami` -a nginx

sudo yum install rabbitmq-server -y
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server


echo "/etc/limited/restartnginx
su devel -c '(cd ~/maven && source ~/.bashrc && nohup ~/maven/run_maven.sh)'" | sudo tee -a /etc/rc.local

sudo echo '#!/bin/bash
systemctl restart nginx' | sudo tee  /etc/limited/restartnginx
sudo chmod a+rx /etc/limited/*

cd ~/maven/scripts_testing_benchmarking/cloud_setup/google/etc/
for x in `ls etc_*`
do
	sudo cp $x /etc/mavenmedical/${x#*_mavenmedical_}
done
sudo chmod 644 /etc/mavenmedical/*

echo MUST SETUP /etc/mavenmedical/maven.config
cd ~
sudo chcon -R -t httpd_user_content_t .
sudo setenforce 1
sudo chmod +x /etc/rc.d/rc.local
mkdir ~/.postgresql
cd .postgresql/
echo user=postgres dbname=maven >> command-line-connect

sudo setsebool -P httpd_read_user_content 1
sudo semanage port -a -t http_port_t -p tcp 8087
sudo semanage port -a -t http_port_t -p tcp 8092
sudo semanage port -a -t http_port_t -p tcp 8088