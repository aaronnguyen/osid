#!/bin/bash

function pause(){
   read -p "$*"
}

echo "===Updating System==="
apt-get update -y
apt-get upgrade -y

echo "===Installing Required Libraries==="
apt-get install python3 python3-pip dcfldd -y
pip3 install cherrypy

echo "===Setup Hostname to osid==="
bash -c "echo 'osid' > /etc/hostname"

echo "===Cloning OSID Project==="
git clone https://github.com/aaronnguyen/osid-python3.git

mkdir /var/osid
mkdir /etc/osid
mkdir /etc/osid/imgroot
cd osid-python3
mv * /etc/osid
cd ..
rm -rf osid-python3

echo "===Installing Apache==="
apt-get install apache2 -y

echo "===Configuring Apache==="
apt-get install php-pear -y
defaultweb='
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /etc/osid/www
    <Directory />
        Options FollowSymLinks
        AllowOverride None
    </Directory>
    <Directory /etc/osid/www/>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride None
        Require all granted
    </Directory>
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride None
        Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    # Possible values include: debug, info, notice, warn, error, crit,
    # alert, emerg.
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>'
echo "$defaultweb" > /etc/apache2/sites-enabled/000-default.conf

bash -c "echo 'ServerName localhost' > /etc/apache2/conf-available/servername.conf"
ln -s /etc/apache2/conf-available/servername.conf /etc/apache2/conf-enabled/servername.conf

echo "===Fixing OSID Settings==="
cd /etc/osid/system
mv server.ini.sample server.ini
mv run_app.sh.sample run_app.sh

sed -i 's/localhost/127.0.0.1/g' server.ini
sed -i 's/80/8080/g' server.ini
sed -i 's/localhost/127.0.0.1/g' server.ini
sed -i 's/\/path_to_folder\/osid-python3/\/etc\/osid/g' server.ini

sed -i 's/cd \/path_to\/py-rpi-dupe/cd \/etc\/osid/g' run_app.sh
sed -i 's/hostname:port/127.0.0.1:8080/g' run_app.sh

sed -i 's/\/home\/pi\/Documents\/py-rpi-dupe/\/etc\/osid/g' osid.desktop.sample

echo "===Make Desktop Icons==="
mv osid.desktop.sample /home/pi/Desktop/osid.desktop
echo "[Desktop Entry]
Name=Root File Manager
Comment=Opens up File Manager with Root Permissions
Icon=/usr/share/pixmaps/gksu-root-terminal.png
Exec=sudo pcmanfm
Type=Application
Encoding=UTF-8
Terminal=false
Categories=None;" > /home/pi/Desktop/RootFileMan.desktop

echo "===Configuring Directory Permissions==="
chown www-data:www-data /etc/osid/imgroot -R
chown www-data:www-data /etc/osid/system -R
chown www-data:www-data /etc/osid/www -R

echo "===Restarting Apache==="
/etc/init.d/apache2 reload
/etc/init.d/apache2 restart

echo "===Setting up Samba==="
apt-get install samba -y

sambasettings="
[global]
workgroup = WORKGROUP
server string = Open Source Image Duplicator
map to guest = Bad User
security = user

log file = /var/log/samba/%m.log
max log size = 50

interfaces = lo eth0
guest account = www-data

dns proxy = no

[Images]
path = /etc/osid/imgroot
public = yes
only guest = yes
writable = yes"
echo "$sambasettings" > /etc/samba/smb.conf


echo "===Restart Your System==="


