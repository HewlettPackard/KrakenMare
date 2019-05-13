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

## Prerequisites

Prerequisites client: RHEL 8 ,**python3 preinstalled** and ssh access  
Prerequisites server: RHEL 8, python3, tar, ansible 2.7.10     
More informations in [/playbooks/README.md](http://o184i024.gre.smktg.hpecorp.net/pathforward/wp1.3/blob/75-deploy-using-ansible-technology/playbooks/README.md)

## Hosts
Example of **hosts** made by CMU

```ini
# PLEASE NOTE: this is an automatically-generated file.

hptc494
n0001
...
n0177
u176i125
u176i126
u176i127
u176i128

[chassis1]
n0001
n0002
n0003
...
n0177

[public]
hptc494
u176i125
u176i126
u176i127
u176i128

[rh8u0_bios]
n0011
...
n0169

```

hosts should be in **/etc/ansible/hosts**  else you need to specify the path with ` -i <PATH> ` in the command line


## Default values

Default values for bdu-client-playbook.yml:
    * ansible_python_interpreter : '/usr/bin/python3'
    * RHEL_Version: rh8rc4_x86_64
    * iso_server: 172.16.7.253
    * iso_source_path: /opt/cmu/repositories
    * iso_mount_point : /opt/cmu/repositories
    * docker_compose_Version : 1.24.0
    * proxy : http://web-proxy.corp.hpecorp.net:8080
    * docker_mirror_registry_address : NULL
    * docker_mirror_registry_port : NULL

Note that you can override values in the command line with ` --extra-vars " <JSON syntax> " `, few examples below .

## Command line

Command line examples:  
**hosts** in --extra-vars is **compulsory**

```bash
ansible-playbook bdu-client-playbook.yml -i /opt/cmu/etc/ansible/hosts --extra-vars "{ hosts : 'all' } "   
# 'all' refer to all keys without section in hosts
```

```bash
ansible-playbook bdu-client-playbook.yml -i /opt/cmu/etc/ansible/hosts --extra-vars "{ hosts : ['chassis1','public','n0170'] , ansible_python_interpreter : '/path/to/python'  , proxy : 'http://web-proxy.corp.hpecorp.net:8080 }"
```
To use a docker mirror registry
```bash
ansible-playbook bdu-client-playbook.yml --extra-vars "{ hosts : 'n0011' ,docker_mirror_registry_address : '172.16.7.253', docker_mirror_registry_port : '5000' }"
```
