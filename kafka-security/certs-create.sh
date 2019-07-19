#!/bin/bash

#set -o nounset \
#    -o errexit \
#    -o verbose \
#    -o xtrace

for tool in keytool openssl
do
    { type $tool &> /dev/null ; } || { echo "$tool needed..." >&2 ; exit 1 ; }
done

# Cleanup files
rm -f *.crt *.csr *_creds *.jks *.srl *.key *.pem *.der *.p12 2> /dev/null 
docker secret rm bd-ca-1.key 2> /dev/null 
docker secret rm bd-ca-1.crt 2> /dev/null 
docker secret rm bd-ca-1.srl 2> /dev/null 

# Generate CA key
openssl req -new -x509 -keyout bd-ca-1.key -out bd-ca-1.crt -days 365 -subj '/CN=ca1.test.hpe.com/OU=BD/O=HPE/L=SanJose/S=Ca/C=US' -passin pass:bluedragon -passout pass:bluedragon || exit 1
docker secret create bd-ca-1.key bd-ca-1.key || exit 1
docker secret create bd-ca-1.crt bd-ca-1.crt || exit 1

for i in broker-1 broker-2 broker-3 schemaregistry connect client
do
	echo "------------------------------- $i -------------------------------"

	# Create host keystore
	keytool -genkey -noprompt \
				 -alias $i \
				 -dname "CN=$i,OU=BD,O=HPE,L=SanJose,S=Ca,C=US" \
                                 -ext "SAN=dns:$i,dns:localhost" \
				 -keystore kafka.$i.keystore.jks \
				 -keyalg RSA \
				 -storepass bluedragon \
				 -keypass bluedragon || exit 1

	# Create the certificate signing request (CSR)
	keytool -keystore kafka.$i.keystore.jks -alias $i -certreq -file $i.csr -storepass bluedragon -keypass bluedragon -ext "SAN=dns:$i,dns:localhost" || exit 1
        #openssl req -in $i.csr -text -noout

        # Sign the host certificate with the certificate authority (CA)
        openssl x509 -req -CA bd-ca-1.crt -CAkey bd-ca-1.key -in $i.csr -out $i-ca1-signed.crt -days 9999 -CAcreateserial -passin pass:bluedragon -extensions v3_req -extfile <(cat <<EOF 
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no
[req_distinguished_name]
CN = $i
[v3_req]
subjectAltName = @alt_names
[alt_names]
DNS.1 = $i
DNS.2 = localhost
EOF
) || exit 1
        #openssl x509 -noout -text -in $i-ca1-signed.crt

        # Sign and import the CA cert into the keystore
	keytool -noprompt -keystore kafka.$i.keystore.jks -alias CARoot -import -file bd-ca-1.crt -storepass bluedragon -keypass bluedragon || exit 1
        #keytool -list -v -keystore kafka.$i.keystore.jks -storepass bluedragon

        # Sign and import the host certificate into the keystore
	keytool -noprompt -keystore kafka.$i.keystore.jks -alias $i -import -file $i-ca1-signed.crt -storepass bluedragon -keypass bluedragon -ext "SAN=dns:$i,dns:localhost" || exit 1
        #keytool -list -v -keystore kafka.$i.keystore.jks -storepass bluedragon

	# Create truststore and import the CA cert
	keytool -noprompt -keystore kafka.$i.truststore.jks -alias CARoot -import -file bd-ca-1.crt -storepass bluedragon -keypass bluedragon || exit 1

	# Save creds
  	echo "bluedragon" > ${i}_sslkey_creds || exit 1
  	echo "bluedragon" > ${i}_keystore_creds || exit 1
  	echo "bluedragon" > ${i}_truststore_creds || exit 1

	# Create pem files and keys used for Schema Registry HTTPS testing
	#   openssl x509 -noout -modulus -in client.certificate.pem | openssl md5
	#   openssl rsa -noout -modulus -in client.key | openssl md5 
    #   echo "GET /" | openssl s_client -connect localhost:8085/subjects -cert client.certificate.pem -key client.key -tls1
	keytool -export -alias $i -file $i.der -keystore kafka.$i.keystore.jks -storepass bluedragon || exit 1
	openssl x509 -inform der -in $i.der -out $i.certificate.pem || exit 1
	keytool -importkeystore -srckeystore kafka.$i.keystore.jks -destkeystore $i.keystore.p12 -deststoretype PKCS12 -deststorepass bluedragon -srcstorepass bluedragon -noprompt || exit 1
	openssl pkcs12 -in $i.keystore.p12 -nodes -nocerts -out $i.key -passin pass:bluedragon || exit 1
	# Create docker secrets for everything
	docker secret rm ${i}_sslkey_creds 2> /dev/null
	docker secret create ${i}_sslkey_creds ${i}_sslkey_creds || exit 1
	docker secret rm ${i}_keystore_creds 2> /dev/null
	docker secret create ${i}_keystore_creds ${i}_keystore_creds || exit 1
	docker secret rm ${i}_truststore_creds 2> /dev/null
	docker secret create ${i}_truststore_creds ${i}_truststore_creds || exit 1
	docker secret rm kafka.$i.keystore.jks 2> /dev/null
	docker secret create kafka.$i.keystore.jks kafka.$i.keystore.jks || exit 1
	docker secret rm kafka.$i.truststore.jks 2> /dev/null
	docker secret create kafka.$i.truststore.jks kafka.$i.truststore.jks || exit 1
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
docker secret create bd-ca-1.srl bd-ca-1.srl || exit 1
docker secret rm broker_jaas.conf 2> /dev/null
docker secret rm zookeeper_jaas.conf 2> /dev/null
docker secret create broker_jaas.conf broker_jaas.conf || exit 1
docker secret create zookeeper_jaas.conf zookeeper_jaas.conf || exit 1