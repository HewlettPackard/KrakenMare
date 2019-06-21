# Dockerfile for building Ansible image for Ubuntu 18.04 (Bionic)

FROM ubuntu:18.04 
RUN apt-get update && apt-get -y upgrade && apt-get install software-properties-common -y && \
    add-apt-repository ppa:ansible/ansible-2.7 && \
    apt-get install ansible -y	
CMD [ "ansible-playbook", "--version" ]
