# Instructions to setup the first server

## Export proxy HPE

```bash
export http_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
export https_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
```

## Setup repo
```bash
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
```

## Setup docker for HPE only
```bash
mkdir -p /etc/systemd/system/docker.service.d/

cat << EOF >  /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=http://web-proxy.corp.hpecorp.net:8080" "HTTPS_PROXY=http://web-proxy.corp.hpecorp.net:8080"
EOF
```
## Setup docker
```bash
systemctl daemon-reload
systemctl restart docker
```
## Bring up sources
```bash
git clone http://o184i024.gre.smktg.hpecorp.net/pathforward/wp1.3.git
cd wp1.3/playbooks/
```

## Run ansible

### Configure hosts files


```ini
[registry]
#Names of registry is mandatory on the third line ( head - 3 | tail -A)
n0498
[supervisory_cloud]
n0498
[injectors]
n0498
...
n0505
[swarm_manager]
n0498
[swarm_nodes]
n0502
....
n0505
```

### Run
```bash
./setup
```
