echo "This server will be setup as the initial master database server."
read -p "Enter the local IP address for THIS server: " MST
read -p "Enter the local IP address of the standby database server: " SBY

#SBY=192.168.1.9
#MST=192.168.1.19

read -p "User Equivalence needs to be set up for the root user before proceeding. Hit enter to continue. ctrl+c to quit."


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#install postgres
#./install.sh $SBY $MST
#ssh $SBY $DIR/install.sh $SBY $MST

#ensure pg is stopped
service postgresql-9.3 stop
ssh $SBY service postgresql-9.3 stop


#setup the master configuration
./master_setup.sh $SBY
./copy_to_standby.sh $SBY
ssh $SBY $DIR/sby_setup.sh $MST
ssh $SBY $DIR/sby_complete.sh

