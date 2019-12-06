#!/bin/bash

#set -o nounset \
#    -o errexit \
#    -o verbose \
#    -o xtrace

for tool in keytool openssl
do
    { type $tool &> /dev/null ; } || { echo "$tool needed..." >&2 ; exit 1 ; }
done

cd /tmp || exit 1

# Cleanup files
rm -f *.crt *.csr *_creds *.pfx *.srl *.key *.pem *.der *.p12 2> /dev/null 

# Generate CA key
openssl req -new -x509 -keyout km-ca-1.key -out km-ca-1.crt -days 365 -subj '/CN=ca1.test.hpe.com/OU=KM/O=HPE/L=SanJose/ST=Ca/C=US' -passin pass:krakenmare -passout pass:krakenmare || exit 1

for i in broker-1 broker-2 broker-3 schemaregistry client mosquittosecu
do
	echo "------------------------------- $i -------------------------------"

	# Create host keystore
	keytool -genkey -noprompt \
				 -alias $i \
				 -dname "CN=$i,OU=KM,O=HPE,L=SanJose,ST=Ca,C=US" \
                                 -ext "SAN=dns:$i,dns:localhost" \
				 -keystore kafka.$i.keystore.pfx \
				 -keyalg RSA -storetype PKCS12 \
				 -storepass krakenmare \
				 -keypass krakenmare || exit 1

	# Create the certificate signing request (CSR)
	keytool -keystore kafka.$i.keystore.pfx -alias $i -certreq -file $i.csr -storepass krakenmare -keypass krakenmare -ext "SAN=dns:$i,dns:localhost" || exit 1

  # Sign the host certificate with the certificate authority (CA)
  openssl x509 -req -CA km-ca-1.crt -CAkey km-ca-1.key -in $i.csr -out $i-ca1-signed.crt -days 9999 -CAcreateserial -passin pass:krakenmare -extensions v3_req -extfile <(cat <<EOF 
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

  # Sign and import the CA cert into the keystore
	keytool -noprompt -keystore kafka.$i.keystore.pfx -alias CARoot -import -file km-ca-1.crt -storepass krakenmare -keypass krakenmare || exit 1

  # Sign and import the host certificate into the keystore
	keytool -noprompt -keystore kafka.$i.keystore.pfx -alias $i -import -file $i-ca1-signed.crt -storepass krakenmare -keypass krakenmare -ext "SAN=dns:$i,dns:localhost" || exit 1

	# Create truststore and import the CA cert
	keytool -noprompt -keystore kafka.$i.truststore.pfx -alias CARoot -import -file km-ca-1.crt -storepass krakenmare -keypass krakenmare || exit 1

	# Save creds
 	echo "krakenmare" > ${i}_sslkey_creds || exit 1
 	echo "krakenmare" > ${i}_keystore_creds || exit 1
 	echo "krakenmare" > ${i}_truststore_creds || exit 1

	# Create pem files and keys used for Schema Registry HTTPS testing
	#   openssl x509 -noout -modulus -in client.certificate.pem | openssl md5
	#   openssl rsa -noout -modulus -in client.key | openssl md5 
  #   echo "GET /" | openssl s_client -connect localhost:8085/subjects -cert client.certificate.pem -key client.key -tls1
	keytool -export -alias $i -file $i.der -keystore kafka.$i.keystore.pfx -storepass krakenmare || exit 1
	openssl x509 -inform der -in $i.der -out $i.certificate.pem || exit 1
	keytool -importkeystore -srckeystore kafka.$i.keystore.pfx -destkeystore $i.keystore.p12 -deststoretype PKCS12 -deststorepass krakenmare -srcstorepass krakenmare -noprompt || exit 1
	openssl pkcs12 -in $i.keystore.p12 -nodes -nocerts -out $i.key -passin pass:krakenmare || exit 1

done
chmod +rw *
