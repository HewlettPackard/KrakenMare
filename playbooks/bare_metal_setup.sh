# Instructions to setup the first server

## Export proxy HPE

export http_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
export https_proxy=http://grewebcachevip.bastion.europe.hp.com:8080

## Setup repo
echo "Mounting repo from 16.16.184.151"
mkdir -p /data/repositories && mount 16.16.184.151:/data/repositories /data/repositories || exit 1
cat << EOF > /etc/yum.repos.d/dvd.repo
[MyRepo2]
name=MyRepo2
baseurl=file:///data/repositories/rh8rc4_x86_64/AppStream
enabled=1
gpgcheck=0

[MyRepo]
name=MyRepo
baseurl=file:///data/repositories/rh8rc4_x86_64/BaseOS
enabled=1
gpgcheck=0
EOF

yum repolist && yum update || exit 1
yum install yum-utils git wget -y || exit 1
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo || exit 1
yum install https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.5-3.1.el7.x86_64.rpm -y || exit 1
yum install docker-ce -y || exit 1

## Setup docker for HPE only
mkdir -p /etc/systemd/system/docker.service.d/ || exit 1

cat << EOF >  /etc/systemd/system/docker.service.d/http-proxy.conf
# BEGIN ANSIBLE MANAGED BLOCK
[Service]
Environment="HTTP_PROXY=http://web-proxy.bbn.hpecorp.net:8080" "HTTPS_PROXY=http://web-proxy.bbn.hpecorp.net:8080"
# END ANSIBLE MANAGED BLOCK
EOF
## Restart docker
systemctl daemon-reload || exit 1
systemctl restart docker || exit 1
## Bring up sources
git clone http://o184i024.gre.smktg.hpecorp.net/pathforward/wp1.3.git || exit 1

## Run ansible

echo "You have to edit the hosts file in /playbook/hosts"
echo "Then run ./setup.sh"
