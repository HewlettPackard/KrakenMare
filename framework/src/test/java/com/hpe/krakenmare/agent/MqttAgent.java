package com.hpe.krakenmare.agent;

import static org.junit.jupiter.api.Assertions.fail;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.impl.MqttUtils;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.RegisterResponse;

public class MqttAgent extends Agent {

	public final static Logger LOG = LoggerFactory.getLogger(MqttAgent.class);

	private final static String NAME = MqttAgent.class.getSimpleName();

	public MqttAgent() {
		super(-1l,
				NAME + "-" + System.currentTimeMillis(),
				null,
				NAME,
				Collections.emptyList());
	}

	public void register(String broker) throws IOException, InterruptedException, MqttException {
		String myAgentTopic = MqttUtils.getRegistrationRequestTopic(this);
		String myManagerTopic = MqttUtils.getRegistrationResponseTopic(this);

		try (MqttClient mqtt = new MqttClient(broker, getUid().toString(), new MemoryPersistence())) {
			MqttConnectOptions connOpts = new MqttConnectOptions();
			LOG.info("Connecting to broker: " + broker);
			mqtt.connect(connOpts);
			LOG.info("Connected");

			CountDownLatch registrationLatch = new CountDownLatch(1);
			mqtt.subscribe(myManagerTopic, (topic, message) -> {
				LOG.info("Message received on topic '" + topic + "': " + message);
				RegisterResponse response = RegisterResponse.fromByteBuffer(ByteBuffer.wrap(message.getPayload()));
				UUID uuid = response.getUuid();
				setUuid(uuid);
				LOG.info("UUID received from manager: " + uuid);
				registrationLatch.countDown();
			});

			RegisterRequest req = new RegisterRequest(getUid(), "test-agent", getName(), "A Java based test agent", false);
			byte[] payload = req.toByteBuffer().array();

			LOG.info("Publishing message '" + new String(payload) + "' to topic '" + myAgentTopic + "'");
			MqttMessage message = new MqttMessage(payload);
			mqtt.publish(myAgentTopic, message);
			LOG.info("Message published");

			try {
				// await registration response
				if (!registrationLatch.await(5, TimeUnit.SECONDS)) {
					fail("No registration response received");
				}
			} finally {
				mqtt.disconnect();
				LOG.info("Disconnected");
			}
		}
	}

}
