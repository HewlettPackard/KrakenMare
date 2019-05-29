cp --archive /root/.ssh/ /root/.ssh_old/
scp 16.19.176.65:/root/.ssh/* /root/.ssh/
cat /root/.ssh-old/authorized_keys >> /root/.ssh/authorized_keys                                                          