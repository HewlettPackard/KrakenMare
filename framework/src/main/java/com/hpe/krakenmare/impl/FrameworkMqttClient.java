package com.hpe.krakenmare.impl;

import java.security.GeneralSecurityException;

import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClientPersistence;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FrameworkMqttClient {

	public final static Logger LOG = LoggerFactory.getLogger(FrameworkMqttClient.class);

	final static String clientId = FrameworkMqttClient.class.getSimpleName();

	// TODO: persist to disk
	MqttClientPersistence persistence = new MemoryPersistence();
	IMqttAsyncClient client;

	public FrameworkMqttClient() {
		// properly release MQTT connection on shutdown
		Runtime.getRuntime().addShutdownHook(new Thread(this::stop));
	}

	public IMqttAsyncClient getClient() {
		return client;
	}

	public void addSubscriber(String topicFilter, IMqttMessageListener messageListener) throws MqttException {
		if (client == null) {
			throw new MqttException(MqttException.REASON_CODE_CLIENT_NOT_CONNECTED);
		}
		IMqttActionListener callback = new IMqttActionListener() {
			@Override
			public void onSuccess(IMqttToken asyncActionToken) {
				LOG.info("New subscriber for topic '" + topicFilter + "': " + messageListener);
			}

			@Override
			public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
				LOG.error("Error while subscribing to topic '" + topicFilter + "': " + messageListener, exception);
			}
		};
		client.subscribe(topicFilter, MqttUtils.getSubscribeQos(), null, callback, messageListener);
	}

	public synchronized void start() throws GeneralSecurityException {
		if (client != null) {
			LOG.warn("Client already started");
			return;
		}
		try {
			String broker = MqttUtils.getBroker();
			client = new MqttAsyncClient(broker, clientId, persistence);
			client.setCallback(new MqttCallback() {
				@Override
				public void messageArrived(String topic, MqttMessage message) throws Exception {
					// LOG.debug("Message received on topic '" + topic + "': " + message);
					LOG.info("Message received on topic '" + topic + "'");
				}

				@Override
				public void deliveryComplete(IMqttDeliveryToken token) {
					// token.getMessage() : "Once the message has been delivered null will be returned"
					// not very useful log then...
					// LOG.debug("Delivery complete for token: " + token);
				}

				@Override
				public void connectionLost(Throwable cause) {
					LOG.warn("Connection lost", cause);
				}
			});

			LOG.info("Connecting to broker: " + broker + " ...");
			MqttConnectOptions connOpts = MqttUtils.getConnectOptions();
			client.connect(connOpts).waitForCompletion();
			LOG.info("Connected to broker: " + broker);
		} catch (MqttException me) {
			LOG.error("Unable to connect", me);
		}
	}

	public synchronized void stop() {
		if (client != null) {
			try {
				LOG.info("Disconnecting...");
				client.disconnect().waitForCompletion();
				client.close();
				client = null;
				LOG.info("Disconnected");
			} catch (MqttException me) {
				LOG.error("Unable to disconnect", me);
			}
		}
	}

}
