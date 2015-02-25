ADMINKEY=$1
LOGACCESSKEY=$2

sudo useradd logaccess -G adm
sudo useradd gateway

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
echo 'command="/usr/bin/ssh -o StrictHostKeyChecking=no logaccess@localhost",no-agent-forwarding,no-port-forwarding,no-user-rc,no-X11-forwarding '"$LOGACCESSKEY"'
command="/usr/bin/ssh -o StrictHostKeyChecking=no devel@localhost",no-agent-forwarding,no-port-forwarding,no-user-rc,no-X11-forwarding '"$ADMINKEY"'
' | sudo su gateway -c "tee ~/.ssh/authorized_keys"
sudo chmod -R 700 ~gateway/.ssh

sudo service sshd restart

#using visudo, add %adm ALL=NOPASSWD: /usr/bin/truecrypt,/etc/limited/restartpostgres,/etc/limited/restartnginx
