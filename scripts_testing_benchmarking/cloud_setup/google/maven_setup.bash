#!/usr/bin/bash
# This script will setup a maven development/test/production environment on a google compute engine or local machine (some additional packages may be required beforehand).
# Before deploying a production machine to Google or any other hosting provider, make sure there is a BAA in place.  We chose Google in large part because of how simple/inexpensive their BAA process was.


# We start by stating pre-requisites, and collection user-supplied information about the desired configuration:

# is gcloud compute set up?  if not, exit
if ! gcloud compute instances list > /dev/null 2>&1 ; then
   echo gcloud compute is not installed/configured properly
   echo search for gcloud compute and install/configure it for your project
   echo in case it doesn't still exist, it is/was google's command line tool for
   echo interacting with their compute engine services, and you may have to 
   echo run equivalent parts of this script manually.
   exit 1
fi

ARCH=
while [[ ! $ARCH =~ ^[sd]$ ]] ; do
      read -n 1 -p 'Will the database and web host be the [s]ame or [d]ifferent machines (s/d)? ' ARCH
      echo
done

if [[ $ARCH =~ ^s$ ]]; then
   read -p 'What name to give this machine instance? ' WEBHOST
   echo
   DBHOST=$WEBHOST
   DBCONHOST=localhost
else
   read -p 'What name to give the web host instance? ' WEBHOST
   echo
   read -p 'What name to give the database instance? ' DBHOST
   echo
   DBCONHOST=$DBHOST
fi

read -p 'What default URL will the web host have? ' WEBURL
echo

echo Select the machine type and region from the following list.  If multiple machines, both will be the same.
gcloud compute machine-types list | grep us-central
read -p 'what machine type (copied from the list)? ' MACHINETYPE
read -p 'what region? ' MACHINEREGION

read -p 'How many GB should the database disk be (recommend at least 100)? ' DISKSIZE

read -p "Maven hosts log realtime events to a designated server so that support personel can get quick insights into what's happening.  It is preferred for this host to be on a different machine.  If you have one designated, enter its name here, otherwise enter 'localhost' " REPORTER

read -p "Maven supports users resetting their own password - but requires a recaptcha first.  Enter two strings separated by a space, the public recaptcha key and then the private key (or leave blank to disable this feature). " RECAPTCHAPUBLIC RECAPTCHAPRIVATE

# our old slack url was https://hooks.slack.com/services/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
read -p 'If you have a slack hook for us to send messages to from the server (a periodic service stops or an unexpected exception is thrown, enter the URL here. ' SLACKURL
if [ -z "$SLACKURL" ]; then
   WRAPEXCEPTION=0
else
   WRAPEXCEPTION=1
fi

LOGLEVEL=
while [[ ! $LOGLEVEL =~ ^[diw]$ ]]; do
      read -n 1 -p 'Enter the log level, [w]arn, [i]nfo, [d]ebug.  Only use debug on a system with *no* access to ephi as some patient information may be logged to an insecure location, which is only allowed for fake patients in a development/test system. ' LOGLEVEL
      echo
done

if [[ $LOGLEVEL =~ ^[d]$ ]]; then
   LOGLEVEL=DEBUG
else
        if [[ $LOGLEVEL =~ ^[i]$ ]]; then
           LOGLEVEL=INFO
        else
           LOGLEVEL=WARN
        fi
fi

PROTOCOL=
while [[ ! $PROTOCOL =~ ^[hsb]$ ]] ; do
      read -n 1 -p 'Support connections from [h]ttp, http[s], or [b]oth (h/s/b)? ' PROTOCOL
      echo
      rm -f nginx.conf
done

if [[ $PROTOCOL =~ ^[sb]$ ]]; then
   while [[ ! ( -r "$WEBSERVERCRT" && -r "$WEBSERVERKEY" ) ]]; do
     read -p 'Enter the filename of the ssl server crt and (unencrypted) server key to be copied to the web host, with the filenames separated by a space ' WEBSERVERCRT WEBSERVERKEY
   done
   ./nginx.conf.bash ssl >> nginx.conf
fi

if [[ $PROTOCOL =~ ^[hb]$ ]]; then
    ./nginx.conf.bash >> nginx.conf
fi

DEPLOYKEY=
while [[ ! -r "$DEPLOYKEY" ]]; do
  read -p 'Enter the filename for the ssh deploykey to pull the software from git ' DEPLOYKEY
done

DBPASSWORD=
while [[ ! $DBPASSWORD =~ ^[ps]$ ]]; do
      read -n 1 -p 'Connection to the database using a [p]assword (insecure) or [s]sl (secure) p/s? ' DBPASSWORD
      echo
done
if [[ $DBPASSWORD =~ p ]]; then
   read -p 'What password? ' DBPASSWORD
   DBEXTRA="password=$DBPASSWORD"
else
   DBPASSWORD=mavendevel
   DBEXTRA="sslmode=verify-ca"
   DBTRUSTEDCA=
   CLIENTTRUSTEDCA=
   DBCERT=
   DBKEY=
   CLIENTCERT=
   CLIENTKEY=
   echo each of the database and web app need a paired cert and key file, as well as a CA cert - the one which signed the others key file
   while [ ! -r "$DBKEY" ]; do
       read -p "Enter the database ssl key filename: " DBKEY
   done
   while [ ! -r "$DBCERT" ]; do
       read -p "Enter the cert for this key: " DBCERT
   done
   while [ ! -r "$CLIENTTRUSTEDCA" ]; do
       read -p "Enter the cert of the authority which signed that key, producing the cert: " CLIENTTRUSTEDCA
   done
   while [ ! -r "$CLIENTKEY" ]; do
       read -p "Enter the psql client ssl key filename: " CLIENTKEY
   done
   while [ ! -r "$CLIENTCERT" ]; do
       read -p "Enter the cert for this key: " CLIENTCERT
   done
   while [ ! -r "$DBTRUSTEDCA" ]; do
       read -p "Enter the cert of the authority which signed that key, producing the cert: " DBTRUSTEDCA
   done
fi

echo "[global]
dbconnection: dbname=maven user=maven host=$DBCONHOST port=5432 $DBEXTRA
reporterhost: $REPORTERHOST
http_addr: $WEBURL
wrap_exception: $WRAPEXCEPTION
slack_url: $SLACKURL
recaptcha_public: $RECAPTCHAPUBLIC
recaptcha_private: $RECAPTCHAPRIVATE" > maven.config

rm -f command-line-connect
echo user=maven dbname=maven host=$DBHOST $DBEXTRA > command-line-connect


./create_new_database_host $DBHOST $MACHINEREGION $MACHINETYPE $DISKSIZE $DEPLOYKEY github_server_fingerprint "$DBPASSWORD" "$DBKEY" "$DBCERT" "$DBTRUSTEDCA"
if [[ $ARCH =~ ^s$ ]]; then
    ./create_new_web_host $WEBHOST $MACHINEREGION "" $DEPLOYKEY github_server_fingerprint "$WEBSERVERCRT" "$WEBSERVERKEY" "$CLIENTKEY" "$CLIENTCERT" "$CLIENTTRUSTEDCA"
else
    ./create_new_web_host $WEBHOST $MACHINEREGION $MACHINETYPE $DEPLOYKEY github_server_fingerprint "$WEBSERVERCRT" "$WEBSERVERKEY" "$CLIENTKEY" "$CLIENTCERT" "$CLIENTTRUSTEDCA"
fi


HARDEN=
while [[ ! $HARDEN =~ ^[ny]$ ]]; do
      read -n 1 -p 'Do you want to significantly limit ssh access to the machine?  This creates a gateway user as the only user with externally allowed access.  It is accessed only with an ssh key, and it only redirects to an administrative user, or a log-access-only user depending on that key.  That redirect only succeeds if you have the proper google authenticator token.  (y/n) ' HARDEN
      echo
done

if [[ $HARDEN =~ ^y$ ]]; then
    while [ -z "$ADMINKEY" ]; do
        read -p 'Enter the administrative user ssh public key ' ADMINKEY
    done
    while [ -z "$LOGACCESSKEY" ]; do
        read -p 'Enter the log access user ssh public key ' LOGACCESSKEY
    done
    for machine in `echo $WEBHOST $DBHOST | xargs -n1 | sort -u`; do
        echo hardening $machine.  to copy down both authenticator keys, and connect by ssh gateway@machine.  your private key will determine which user you log in as
        gcloud compute copy-files --zone $MACHINEREGION setup_scripts/harden.sh $machine:
        gcloud compute ssh $machine --zone $MACHINEREGION --ssh-flag="-t" --command "bash harden.sh \"$ADMINKEY\" \"$LOGACCESSKEY\""
    done
fi

