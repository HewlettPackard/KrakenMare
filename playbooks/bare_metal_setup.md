# Instructions to setup the first server

## Export proxy HPE
```bash
export http_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
export https_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
```
## Setup repo
```bash
mkdir -p /opt/cmu/repositories && mount 172.16.7.253:/opt/cmu/repositories /opt/cmu/repositories || exit 1
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
```

```bash
yum repolist && yum update || exit 1
yum install yum-utils git wget -y || exit 1
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo || exit 1
yum install https://download.docker.com/linux/centos/7/x86_64/stable/Packages/containerd.io-1.2.5-3.1.el7.x86_64.rpm -y || exit 1
yum install docker-ce -y || exit 1
```

## Setup docker for HPE only
```bash
mkdir -p /etc/systemd/system/docker.service.d/ || exit 1

cat << EOF >  /etc/systemd/system/docker.service.d/http-proxy.conf
# BEGIN ANSIBLE MANAGED BLOCK
[Service]
Environment="HTTP_PROXY=http://web-proxy.corp.hpecorp.net:8080" "HTTPS_PROXY=http://web-proxy.corp.hpecorp.net:8080"
# END ANSIBLE MANAGED BLOCK
EOF
```
## Restart docker
```bash
systemctl daemon-reload || exit 1
systemctl restart docker || exit 1
```
## Bring up sources
```bash
git clone http://o184i024.gre.smktg.hpecorp.net/pathforward/wp1.3.git || exit 1
```