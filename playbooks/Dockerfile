# Dockerfile for building Ansible image for Ubuntu 18.04 (Bionic)

FROM ubuntu:18.04 
RUN apt-get update && apt-get -y upgrade  && \
	apt-get install -y curl python-packaging python-setuptools make ssh sshpass && \
	curl https://codeload.github.com/ansible/ansible/tar.gz/v2.7.10 --output ansible.tar.gz && \
	tar xvf ansible.tar.gz && \
	cd ansible-2.7.10 && \
	make install && \
	rm -rf ansible.tar.gz ansible-2.7.10 && \
	apt-get remove --purge curl  make -y
CMD [ "ansible-playbook", "--version" ]
