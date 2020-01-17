package com.hpe.krakenmare.impl;

import java.net.Socket;
import java.security.GeneralSecurityException;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.util.UUID;

import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLEngine;
import javax.net.ssl.TrustManager;
import javax.net.ssl.X509ExtendedTrustManager;

import org.eclipse.paho.client.mqttv3.MqttConnectOptions;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.core.Agent;

public class MqttUtils {

	public static final UUID EMPTY_UUID = UUID.fromString("00000000-0000-0000-0000-000000000000");

	private static final String REGISTRATION_TOPIC = Main.getProperty("km.agent-registration.mqtt.topic");
	private static final String SENSOR_LIST_TOPIC = Main.getProperty("km.device-registration.mqtt.topic");

	/* Registration */

	public static String getRegistrationRequestTopic() {
		return REGISTRATION_TOPIC + "/+/request";
	}

	// use "uid" here since the agent doesn't know yet its UUID so can't listen to it
	public static String getRegistrationRequestTopic(Agent agent) {
		return REGISTRATION_TOPIC + "/" + agent.getUid() + "/request";
	}

	// use "uid" here since the agent doesn't know yet its UUID so can't listen to it
	public static String getRegistrationResponseTopic(Agent agent) {
		return getRegistrationResponseTopic(agent.getUid());
	}

	// use "uid" here since the agent doesn't know yet its UUID so can't listen to it
	public static String getRegistrationResponseTopic(CharSequence uid) {
		return REGISTRATION_TOPIC + "/" + uid + "/response";
	}

	/* Sensor List */

	public static String getSensorListRequestTopic() {
		return SENSOR_LIST_TOPIC + "/+/request";
	}

	public static String getSensorListRequestTopic(Agent agent) {
		return SENSOR_LIST_TOPIC + "/" + agent.getUuid() + "/request";
	}

	public static String getSensorListResponseTopic(Agent agent) {
		return getSensorListResponseTopic(agent.getUuid());
	}

	public static String getSensorListResponseTopic(UUID uuid) {
		return SENSOR_LIST_TOPIC + "/" + uuid + "/response";
	}

	public static String getBroker() {
		return Main.getProperty("mqtt.server");
	}

	public static boolean isBrokerSecured() {
		return getBroker().startsWith("ssl://");
	}

	public static MqttConnectOptions getConnectOptions() throws GeneralSecurityException {
		MqttConnectOptions connOpts = new MqttConnectOptions();
		if (isBrokerSecured()) {
			// TODO: need to get rid of this by properly setup certificates, keystore, etc.
			MqttUtils.setUpTrustAllCerts();
			connOpts.setSocketFactory(SSLContext.getDefault().getSocketFactory());
		}
		connOpts.setAutomaticReconnect(true);
		connOpts.setCleanSession(false);
		return connOpts;
	}

	// hacky method to pass through hostname validation
	// TODO: NEEDS TO EVENTUALLY BE REMOVED
	// the proper method is likely to import the MQTT broker cert into this JVM trustore
	// see https://stackoverflow.com/questions/2893819/accept-servers-self-signed-ssl-certificate-in-java-client/2893932#2893932
	private static void setUpTrustAllCerts() throws GeneralSecurityException {
		TrustManager[] trustAllCerts = new TrustManager[] { new X509ExtendedTrustManager() {
			@Override
			public java.security.cert.X509Certificate[] getAcceptedIssuers() {
				return null;
			}

			@Override
			public void checkServerTrusted(java.security.cert.X509Certificate[] chain, String authType) throws CertificateException {
			}

			@Override
			public void checkClientTrusted(java.security.cert.X509Certificate[] chain, String authType) throws CertificateException {
			}

			@Override
			public void checkClientTrusted(X509Certificate[] chain, String authType, Socket socket) throws CertificateException {
			}

			@Override
			public void checkServerTrusted(X509Certificate[] chain, String authType, Socket socket) throws CertificateException {
			}

			@Override
			public void checkClientTrusted(X509Certificate[] chain, String authType, SSLEngine engine) throws CertificateException {
			}

			@Override
			public void checkServerTrusted(X509Certificate[] chain, String authType, SSLEngine engine) throws CertificateException {
			}
		} };

		SSLContext sc = SSLContext.getInstance("SSL");
		sc.init(null, trustAllCerts, new java.security.SecureRandom());
		SSLContext.setDefault(sc);
	}
}
