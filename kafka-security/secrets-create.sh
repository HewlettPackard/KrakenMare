#!/bin/bash

set -x

#set -o nounset \
#    -o errexit \
#    -o verbose \
#    -o xtrace

# Cleanup files
docker secret rm km-ca-1.key 2> /dev/null 
docker secret rm km-ca-1.crt 2> /dev/null 
docker secret rm km-ca-1.srl 2> /dev/null 

# Generate CA key
docker secret create km-ca-1.key km-ca-1.key || exit 1
docker secret create km-ca-1.crt km-ca-1.crt || exit 1

for i in broker-1 broker-2 broker-3 schemaregistry connect client
do
	echo "------------------------------- $i -------------------------------"

	# Create docker secrets for everything
	docker secret rm ${i}_sslkey_creds 2> /dev/null
	docker secret create ${i}_sslkey_creds ${i}_sslkey_creds || exit 1
	docker secret rm ${i}_keystore_creds 2> /dev/null
	docker secret create ${i}_keystore_creds ${i}_keystore_creds || exit 1
	docker secret rm ${i}_truststore_creds 2> /dev/null
	docker secret create ${i}_truststore_creds ${i}_truststore_creds || exit 1
	docker secret rm kafka.$i.keystore.pfx 2> /dev/null
	docker secret create kafka.$i.keystore.pfx kafka.$i.keystore.pfx || exit 1
	docker secret rm kafka.$i.truststore.pfx 2> /dev/null
	docker secret create kafka.$i.truststore.pfx kafka.$i.truststore.pfx || exit 1
	docker secret rm $i-ca1-signed.crt 2> /dev/null
	docker secret create $i-ca1-signed.crt $i-ca1-signed.crt || exit 1
	docker secret rm $i.keystore.p12 2> /dev/null
	docker secret create $i.keystore.p12 $i.keystore.p12 || exit 1
	docker secret rm $i.key 2> /dev/null
	docker secret create $i.key $i.key || exit 1
	docker secret rm $i.certificate.pem 2> /dev/null
	docker secret create $i.certificate.pem $i.certificate.pem || exit 1
	docker secret rm $i.der 2> /dev/null
	docker secret create $i.der $i.der || exit 1
	docker secret rm $i.csr 2> /dev/null
	docker secret create $i.csr $i.csr || exit 1

done
docker secret create km-ca-1.srl km-ca-1.srl || exit 1
docker secret rm broker_jaas.conf 2> /dev/null
docker secret rm zookeeper_jaas.conf 2> /dev/null
docker secret create broker_jaas.conf broker_jaas.conf || exit 1
docker secret create zookeeper_jaas.conf zookeeper_jaas.conf || exit 1


