#!/bin/bash
sudo yum install pcre-devel zlib-devel openssl-devel gcc libpqxx-devel libpqxx libffi-devel policycoreutils-python-2.2.5-11.el7_0.1.x86_64 nodejs python-psycopg2 -y

echo "export MAVEN_ROOT=~/maven
export PYTHONPATH=$MAVEN_ROOT" >> .bashrc
source ~/.bashrc

cd

cp ~/maven/scripts_testing_benchmarking/gitHooks/cloudBoxes/* .git/hooks/
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
sudo chmod 400 /etc/nginx/conf.d/server.*
sudo rm /etc/nginx/nginx.conf /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/example_ssl.conf
sudo cp ~/nginx.conf /etc/nginx/conf.d/
sudo cp ~/nginx.base.conf /etc/nginx/nginx.conf
chmod g+rx `pwd`

sudo usermod -G `whoami` -a nginx
sudo systemctl start nginx
cd ~/maven/app/frontend_web/nodejs/ && node r.js -o build.js && cd

sudo yum install rabbitmq-server -y
sudo chown -R rabbitmq:rabbitmq /var/log/rabbitmq
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

cd ~
sudo chcon -R -t httpd_user_content_t .
sudo setenforce 1
sudo chmod +x /etc/rc.d/rc.local
mkdir ~/.postgresql
mv command-line-connect .postgresql
if [ -r postgresql.crt ]; then
    mv postgresql.crt postgresql.key root.crt .postgresql
fi

sudo setsebool -P httpd_read_user_content 1
sudo semanage port -a -t http_port_t -p tcp 8087
sudo semanage port -a -t http_port_t -p tcp 8092
sudo semanage port -a -t http_port_t -p tcp 8088
sudo semanage port -a -t amqp_port_t -p tcp 25672
sudo systemctl start rabbitmq-server

cd ~/maven/scripts_testing_benchmarking/gitHooks/cloudBoxes
./explicit-db-update
cd ~/maven
nohup ./run_maven.sh

