## To install ansible on server node

## For HPE intranet network only 
```bash
 export http_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
 export https_proxy=http://grewebcachevip.bastion.europe.hp.com:8080

```
## Step 1 Add dvd sources
```bash
mkdir -p /data/repositories && mount 16.16.184.151:/data/repositories /data/repositories
```

Update repo list.
Create a file named dvd.repo in /etc/yum.repos.d
```bash
touch /etc/yum.repos.d/dvd.repo
```
Add these lines to dvd.repo
```bash
[MyRepo2]
name=MyRepo2
baseurl=file:///data/repositories/rh8rc2_x86_64/AppStream
enabled=1
gpgcheck=0

[MyRepo]
name=MyRepo
baseurl=file:///data/repositories/rh8rc2_x86_64/BaseOS
enabled=1
gpgcheck=0
```

```bash
yum repolist && yum update
```




## Step 2 Compile Ansible from source
```bash
yum --assumeyes install tar python36

update-alternatives --config python
#Then choose /usr/bin/python3
pip3.6 install packaging

cd ~/
curl https://codeload.github.com/ansible/ansible/tar.gz/v2.7.10 --output ansible-2.7.10.tar.gz
tar xvf ansible-2.7.10.tar.gz && rm -rf ansible-2.7.10.tar.gz 
cd ansible-2.7.10/ && make install
cd ../ && rm -rf ansible-2.7.10/

```

