#!/bin/bash

echo "[*] Setting Hostname..."
echo "[*][*] Writing to /etc/hosts"
cat > /etc/hosts <<- EOF
127.0.0.1       localhost
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters

127.0.1.1       LongRangeReader
EOF

hostname LongRangeReader

echo "[*][*] Writing to /etc/hostname"
echo "LongRangeReader" > /etc/hostname;


echo "[*] Installing Packages..."
apt-get update;
apt-get install -y git screen pigpio python-pip isc-dhcp-server hostapd;
pip install tornado pigpio;


echo "[*] Writing Configs..."

echo "[*][*] Writing to /etc/network/interfaces"
cat > /etc/network/interfaces <<- EOM
auto lo
iface lo inet loopback

iface eth0 inet manual

allow-hotplug wlan0
iface wlan0 inet static
        post-up /usr/sbin/hostapd -B /etc/hostapd/hostapd.conf
        post-up service isc-dhcp-server restart
        address 192.168.3.1
        netmask 255.255.255.0
EOM

echo "[*][*] Writing to /etc/dhcp/dhcpd.conf"
cat > /etc/dhcp/dhcpd.conf <<- EOM
ddns-update-style none;
default-lease-time 600;
max-lease-time 7200;
authoritative;
log-facility local7;

subnet 192.168.3.0 netmask 255.255.255.0 {
    range 192.168.3.2 192.168.3.50;
    option broadcast-address 192.168.3.255;
    option routers 192.168.3.1;
    default-lease-time 600;
    max-lease-time 7200;
    option domain-name "local";
    option domain-name-servers 8.8.8.8, 8.8.4.4;
}
EOM

echo "[*][*] Writing to /etc/default/isc-dhcp-server"
cat > /etc/default/isc-dhcp-server <<- EOM
INTERFACES="wlan0"
EOM

echo "[*][*] Writing to /etc/hostapd/hostapd.conf"
cat > /etc/hostapd/hostapd.conf <<- EOM
interface=wlan0
driver=nl80211
ssid=LongRangeReader
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=accessgranted
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOM

echo "[*][*] Writing to /etc/default/hostapd"
cat > /etc/default/hostapd <<- EOM
DAEMON_OPTS="/etc/hostapd/hostapd.conf"
EOM


echo "[*] Writing boot files - /etc/rc.local"
cat > /etc/rc.local <<- EOM
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=\$(hostname -I) || true
if [ "\$_IP" ]; then
  printf "My IP address is %s\n" "\$_IP"
fi

# Start pigpio daemon
pigpiod

# Start long range reader script
screen -dmS lrr_wiegand_listener bash -c "cd /opt/LongRangeReader; su -c 'python ./lrr_wiegand_listener.py'"
screen -dmS lrr_webserver bash -c "cd /opt/LongRangeReader; su -c 'python ./lrr_webserver.py'"
exit 0
EOM


echo "[*] Installing LongRangeReader code to /opt/LongRangeReader/..."
mkdir /opt/;
cd /opt/;
#git clone git@github.com:linuz/LongRangeReader.git
mkdir LongRangeReader; cd /opt/LongRangeReader/; rm /opt/LongRangeReader/*; wget http://192.168.0.5:8000/lrr_webserver.py; wget http://192.168.0.5:8000/lrr_wiegand_listener.py;


echo "[*] Enabling hostapd on startup"
sudo update-rc.d hostapd defaults


echo "[*] Restarting Raspberry Pi in 10 seconds."
sleep 10;
reboot