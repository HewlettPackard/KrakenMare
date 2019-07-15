#!/bin/bash

#set -o nounset \
#    -o errexit \
#    -o verbose \
#    -o xtrace

# Cleanup files
rm -f *.crt *.csr *_creds *.jks *.srl *.key *.pem *.der *.p12
docker secret rm bd-ca-1.key
docker secret rm bd-ca-1.crt
docker secret rm bd-ca-1.srl

# Generate CA key
openssl req -new -x509 -keyout bd-ca-1.key -out bd-ca-1.crt -days 365 -subj '/CN=ca1.test.hpe.com/OU=BD/O=HPE/L=SanJose/S=Ca/C=US' -passin pass:bluedragon -passout pass:bluedragon
docker secret create bd-ca-1.key bd-ca-1.key
docker secret create bd-ca-1.crt bd-ca-1.crt

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
				 -keypass bluedragon

	# Create the certificate signing request (CSR)
	keytool -keystore kafka.$i.keystore.jks -alias $i -certreq -file $i.csr -storepass bluedragon -keypass bluedragon -ext "SAN=dns:$i,dns:localhost"
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
)
        #openssl x509 -noout -text -in $i-ca1-signed.crt

        # Sign and import the CA cert into the keystore
	keytool -noprompt -keystore kafka.$i.keystore.jks -alias CARoot -import -file bd-ca-1.crt -storepass bluedragon -keypass bluedragon
        #keytool -list -v -keystore kafka.$i.keystore.jks -storepass bluedragon

        # Sign and import the host certificate into the keystore
	keytool -noprompt -keystore kafka.$i.keystore.jks -alias $i -import -file $i-ca1-signed.crt -storepass bluedragon -keypass bluedragon -ext "SAN=dns:$i,dns:localhost"
        #keytool -list -v -keystore kafka.$i.keystore.jks -storepass bluedragon

	# Create truststore and import the CA cert
	keytool -noprompt -keystore kafka.$i.truststore.jks -alias CARoot -import -file bd-ca-1.crt -storepass bluedragon -keypass bluedragon

	# Save creds
  	echo "bluedragon" > ${i}_sslkey_creds
  	echo "bluedragon" > ${i}_keystore_creds
  	echo "bluedragon" > ${i}_truststore_creds

	# Create pem files and keys used for Schema Registry HTTPS testing
	#   openssl x509 -noout -modulus -in client.certificate.pem | openssl md5
	#   openssl rsa -noout -modulus -in client.key | openssl md5 
    #   echo "GET /" | openssl s_client -connect localhost:8085/subjects -cert client.certificate.pem -key client.key -tls1
	keytool -export -alias $i -file $i.der -keystore kafka.$i.keystore.jks -storepass bluedragon
	openssl x509 -inform der -in $i.der -out $i.certificate.pem
	keytool -importkeystore -srckeystore kafka.$i.keystore.jks -destkeystore $i.keystore.p12 -deststoretype PKCS12 -deststorepass bluedragon -srcstorepass bluedragon -noprompt
	openssl pkcs12 -in $i.keystore.p12 -nodes -nocerts -out $i.key -passin pass:bluedragon
	# Create docker secrets for everything
	docker secret rm ${i}_sslkey_creds
	docker secret create ${i}_sslkey_creds ${i}_sslkey_creds
	docker secret rm ${i}_keystore_creds
	docker secret create ${i}_keystore_creds ${i}_keystore_creds
	docker secret rm ${i}_truststore_creds
	docker secret create ${i}_truststore_creds ${i}_truststore_creds
	docker secret rm kafka.$i.keystore.jks
	docker secret create kafka.$i.keystore.jks kafka.$i.keystore.jks
	docker secret rm kafka.$i.truststore.jks
	docker secret create kafka.$i.truststore.jks kafka.$i.truststore.jks
	docker secret rm $i-ca1-signed.crt
	docker secret create $i-ca1-signed.crt $i-ca1-signed.crt
	docker secret rm $i.keystore.p12
	docker secret create $i.keystore.p12 $i.keystore.p12
	docker secret rm $i.key
	docker secret create $i.key $i.key
	docker secret rm $i.certificate.pem
	docker secret create $i.certificate.pem $i.certificate.pem
	docker secret rm $i.der
	docker secret create $i.der $i.der
	docker secret rm $i.csr
	docker secret create $i.csr $i.csr

done
docker secret create bd-ca-1.srl bd-ca-1.srl
docker secret rm broker_jaas.conf
docker secret rm zookeeper_jaas.conf
docker secret create broker_jaas.conf broker_jaas.conf
docker secret create zookeeper_jaas.conf zookeeper_jaas.conf
