sudo useradd logaccess -G adm
sudo useradd gateway
sudo userdel -r tdubois

# install google authenticator
sudo yum install bzip2 wget pam-devel gcc -y
#sudo yum groupinstall "Development Tools" -y
wget https://google-authenticator.googlecode.com/files/libpam-google-authenticator-1.0-source.tar.bz2
bunzip2 libpam-google-authenticator-1.0-source.tar.bz2
tar -xvf libpam-google-authenticator-1.0-source.tar
rm -f libpam-google-authenticator-1.0-source.tar
cd libpam-google-authenticator-1.0
make -j 4
sudo make install
echo 'auth  required  pam_google_authenticator.so secret=/home/${USER}/.ssh/.google_authenticator' | sudo tee -a /etc/pam.d/sshd
sudo sed -i.bak 's/ChallengeResponseAuthentication no/ChallengeResponseAuthentication yes/' /etc/ssh/sshd_config

# 2 factor for logaccess
sudo su logaccess -c "mkdir ~/.ssh"
sudo su logaccess -c "/usr/local/bin/google-authenticator -t -d -w 3 -r 3 -R 30 -s ~/.ssh/.google_authenticator -f"
sudo su logaccess -c "restorecon -R -v ~/.ssh"
# 2 factor for devel
/usr/local/bin/google-authenticator -t -d -w 3 -r 3 -R 30 -s ~/.ssh/.google_authenticator -f

echo "logaccess:mavendevel
devel:mavendevel" | sudo chpasswd

echo "
AllowUsers logaccess@localhost devel@localhost gateway

Match User logaccess,devel
      PasswordAuthentication yes
 
" | sudo tee -a /etc/ssh/sshd_config


# no new users
sudo chmod 555 /home

# set gateway's ssh permissions
sudo su gateway -c "mkdir ~/.ssh"
echo 'command="/usr/bin/ssh -o StrictHostKeyChecking=no logaccess@localhost",no-agent-forwarding,no-port-forwarding,no-user-rc,no-X11-forwarding ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAqCHiOtTO2dj9nySwNVwgSxeEmbla3C8ss5K+QyT2BjHR0Zag2Lkgenqla8sYkQSs3lEUEloL57c45JTGl62a00VOIBXrTqNZoxd+w0Pis5OLoLhzFE91N4CQq0ouybwMQgfaF50pRMmJ2RUEgI77EVW7mLXjjcqL8cerHHm/w9H4cCtWptrabOEWtUI6CmoVsodaA4JH82qvnIXHaEyjjE9i8wdGU5YsXKUvBxBO+lJdjAisUn2wSS81zvT4hrUJltzHaUYOxCKD8778WfBSj4nm/XJkcwh4BHaJyMYClwiHNkmlh2Z863tFZLBLpM/0tonAf/mbH/yMqrmvJI7M7w== tom@mavenmedical.net
command="/usr/bin/ssh -o StrictHostKeyChecking=no devel@localhost",no-agent-forwarding,no-port-forwarding,no-user-rc,no-X11-forwarding ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA7eAnZKvO653gDXel6ms1JuXT+83bkGeokgxOpN/c2+M9GAzk84sKq7iL3hwu+0+stRjazEaLWDP79DKmugqvXeTLZTJqoG0EbYCdMDl8CPTQnOlFiliFJaE1lsvC28UVqElDwgIYaPM7fSXrsCWm8TlPkTswmWSIqlMqjZNJq4+KKLO/YQ8AqU1xCNsvs/GIABcED4Qcf0Sf3YxGVf90TC7bdcYj3OmT7XooVGJbXIdMcEoiIP3QrNUdGDmz6upGAkI59HVKww1pyFFPHsTVBxdLl51QxI06Ai5Ve5a/a84YUrmNzHIeAuQyzKOLxL2lT+tT5f8kQ+2pUBhLF7Z7Cw== devel@remote.mavenmedical.net
' | sudo su gateway -c "tee ~/.ssh/authorized_keys"
sudo chmod -R 700 ~gateway/.ssh

sudo service sshd restart

#using visudo, add %adm ALL=NOPASSWD: /usr/bin/truecrypt,/etc/limited/restartpostgres,/etc/limited/restartnginx
