# Instructions to setup the first server

## Export proxy HPE

export http_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
export https_proxy=http://grewebcachevip.bastion.europe.hp.com:8080

## Setup repo
mkdir -p /opt/cmu/repositories && mount 172.16.7.253:/opt/cmu/repositories /opt/cmu/repositories
cat << EOF > /etc/yum.repos.d/dvd.repo
[MyRepo2]
name=MyRepo2
baseurl=file:///opt/cmu/repositories/rh8rc4_x86_64/AppStream
enabled=1
gpgcheck=0

[MyRepo]
name=MyRepo
baseurl=file:///opt/cmu/repositories/rh8rc4_x86_64/BaseOS
enabled=1
gpgcheck=0
EOF

yum repolist && yum update
yum install yum-utils git -y
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.5-3.1.el7.x86_64.rpm -y
yum install docker-ce -y

## Setup docker for HPE only
mkdir -p /etc/systemd/system/docker.service.d/

cat << EOF >  /etc/systemd/system/docker.service.d/http-proxy.conf
# BEGIN ANSIBLE MANAGED BLOCK
[Service]
Environment="HTTP_PROXY=http://web-proxy.corp.hpecorp.net:8080" "HTTPS_PROXY=http://web-proxy.corp.hpecorp.net:8080"
# END ANSIBLE MANAGED BLOCK
EOF
## Restart docker
systemctl daemon-reload
systemctl restart docker
## Bring up sources
git clone http://o184i024.gre.smktg.hpecorp.net/pathforward/wp1.3.git
cd wp1.3/playbooks/

## Run ansible

echo "You have to edit the hosts file in /playbook/hosts"
echo "Then run ./setup.sh"
