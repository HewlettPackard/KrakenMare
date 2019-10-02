package com.hpe.krakenmare.impl;

import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttClientPersistence;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.Main;

public class FrameworkMqttListener {

	public final static Logger LOG = LoggerFactory.getLogger(FrameworkMqttListener.class);

	final static String broker = "tcp://" + Main.getProperty("mqtt.server"); // "tcp://mosquitto:1883";
	final static String clientId = FrameworkMqttListener.class.getSimpleName();

	// TODO: persist to disk
	MqttClientPersistence persistence = new MemoryPersistence();
	// TODO: make client async
	IMqttClient client;

	public FrameworkMqttListener() {
		// properly release MQTT connection on shutdown
		Runtime.getRuntime().addShutdownHook(new Thread(this::stop));
	}

	public IMqttClient getClient() {
		return client;
	}

	public void addSubscriber(String topicFilter, IMqttMessageListener messageListener) throws MqttException {
		if (client == null) {
			throw new MqttException(MqttException.REASON_CODE_CLIENT_NOT_CONNECTED);
		}
		client.subscribe(topicFilter, messageListener);
		LOG.info("New subscriber for topic '" + topicFilter + "': " + messageListener);
	}

	public synchronized void start() {
		if (client != null) {
			LOG.warn("Client already started");
			return;
		}
		try {
			client = new MqttClient(broker, clientId, persistence);

			MqttConnectOptions connOpts = new MqttConnectOptions();
			connOpts.setAutomaticReconnect(true);
			// connOpts.setCleanSession(true);

			LOG.info("Connecting to broker: " + broker + " ...");
			// IMqttToken token = client.connect(connOpts);
			// token.waitForCompletion();
			client.connect(connOpts);
			LOG.info("Connected to broker: " + broker);
		} catch (MqttException me) {
			LOG.error("Unable to connect to MQTT", me);
		}
	}

	public synchronized void stop() {
		if (client != null) {
			try {
				LOG.info("Disconnecting...");
				client.disconnect();
				client.close();
				client = null;
				LOG.info("Disconnected");
			} catch (MqttException me) {
				LOG.error("Unable to disconnect from MQTT", me);
			}
		}
	}

}
