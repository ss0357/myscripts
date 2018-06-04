#!/bin/sh
rm -rf /tmp/.X*
sleep 2

#ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
#mkdir -p /var/run/radiusd/
#chmod 777  /var/run/radiusd

cd /home/atxuser
su atxuser -c "vncserver"
/usr/sbin/sshd -p 1022 -D