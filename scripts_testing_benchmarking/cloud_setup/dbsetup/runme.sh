echo "This server will be setup as the initial master database server."
read -p "Enter the local IP address for THIS server to setup a master database (or just enter for standby only): " MST
read -p "Enter the local IP address of the standby database server (or just enter for local only): " SBY

#SBY=192.168.1.9
#MST=192.168.1.19

read -p "User Equivalence needs to be set up for the root user before proceeding. Hit enter to continue. ctrl+c to quit."


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#install postgres
#./install.sh $SBY $MST
#ssh $SBY $DIR/install.sh $SBY $MST

#ensure pg is stopped
service postgresql-9.3 stop
if [ -n "$SBY" ]; then
  ssh $SBY service postgresql-9.3 stop
fi

#setup the master configuration
if [ -n "$MST" ]; then
  ./master_setup.sh $SBY
fi 

#prep the standby server
if [ -n "$SBY" ]; then
  if [ -n "$MST" ]; then 
    MST=ifconfig |grep "addr:"|head -n 1|cut -d ":" -f2|cut -d " " -f1
  fi
  echo "About to create a standby database on $SBY."
  echo "This command should ONLY be run from the master node."
  read -p "Hit enter to continue. (Only continue from the master node)"
  ./copy_to_standby.sh $SBY
  ssh $SBY $DIR/sby_setup.sh $MST
  ssh $SBY $DIR/sby_complete.sh
fi

