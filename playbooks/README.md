# To install ansible on server node

## For HPE intranet network only
```bash
 export http_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
 export https_proxy=http://grewebcachevip.bastion.europe.hp.com:8080
```
## 1. Add dvd sources
```bash
mkdir -p /data/repositories && mount 16.16.184.151:/data/repositories /data/repositories
```

Update repo list.
Create a file named dvd.repo in /etc/yum.repos.d
```bash
cat << EOF > /etc/yum.repos.d/dvd.repo
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
EOF
```
Update packages list
```bash
yum repolist && yum update
```




## 2. Compile Ansible from source
Install tar
```bash
yum --assumeyes install tar
```
Change alternatives for python
```bash
update-alternatives --set python /usr/bin/python3
```

```bash
pip3.6 install packaging
```
Compile
```bash
cd ~/
curl https://codeload.github.com/ansible/ansible/tar.gz/v2.7.10 --output ansible-2.7.10.tar.gz
tar xvf ansible-2.7.10.tar.gz && rm -rf ansible-2.7.10.tar.gz
cd ansible-2.7.10/ && make install
cd ../ && rm -rf ansible-2.7.10/
```


---

# To deploy the ansible playbooks
Prerequisites client: RHEL 8 and **python3 preinstalled**    
Prerequisites server: RHEL 8, python3, tar, ansible .  
You need an host file on the server node:  
**hosts**   
```ini 
[bdu-client]
16.19.176.125 ansible_python_interpreter=/usr/bin/python3  
16.19.176.126 ansible_python_interpreter=/usr/bin/python3  

```

hosts should be in **/etc/ansible/hosts**  else you need to specify the path with -i <PATH> in the command line



If the client is a docker registry
```bash
ansible-playbook bdu-client-playbook.yml -i hosts
```
else you need to specify mirror registry adress and port
```bash
ansible-playbook bdu-client-playbook.yml -i hosts --extra-vars "{docker_mirror_registry_adress : '16.19.176.126', docker_mirror_registry_port : '5000'}"
```

Others extra-variables you can specify :  

* RHEL_Version : rh8rc4_x86_64
* iso_server : 16.16.184.151
* docker_compose_Version : 1.24.0