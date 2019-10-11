package com.hpe.krakenmare.agent;

import static org.junit.jupiter.api.Assertions.assertNotNull;
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
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.impl.FrameworkMqttClient;
import com.hpe.krakenmare.impl.MqttRegistrationListener;
import com.hpe.krakenmare.impl.MqttUtils;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.RegisterResponse;
import com.hpe.krakenmare.repositories.AgentMemoryRepository;

public class MqttAgentTest {

	public final static Logger LOG = LoggerFactory.getLogger(MqttAgentTest.class);

	static String broker = "tcp://" + Main.getProperty("mqtt.server"); // "tcp://mosquitto:1883";

	private final String myName = MqttAgentTest.class.getSimpleName();
	private final String myId = myName + "-" + System.currentTimeMillis();

	@BeforeEach
	public void setup() throws MqttException {
		FrameworkMqttClient listener = new FrameworkMqttClient();
		listener.start();

		AgentMemoryRepository agents = new AgentMemoryRepository();
		MqttRegistrationListener.registerNew(listener, agents);
	}

	@Test
	public void register() throws IOException, InterruptedException, MqttException {
		Agent agent = new Agent(-1l, myId, null, myName, Collections.emptyList());
		String myAgentTopic = MqttUtils.getRegistrationRequestTopic(agent);
		String myManagerTopic = MqttUtils.getRegistrationResponseTopic(agent);

		try (MqttClient mqtt = new MqttClient(broker, myId, new MemoryPersistence())) {
			MqttConnectOptions connOpts = new MqttConnectOptions();
			LOG.info("Connecting to broker: " + broker);
			mqtt.connect(connOpts);
			LOG.info("Connected");

			CountDownLatch registrationLatch = new CountDownLatch(1);
			mqtt.subscribe(myManagerTopic, (topic, message) -> {
				LOG.info("Message received on topic '" + topic + "': " + message);
				RegisterResponse response = RegisterResponse.fromByteBuffer(ByteBuffer.wrap(message.getPayload()));
				UUID uuid = response.getUuid();
				agent.setUuid(uuid);
				LOG.info("UUID received from manager: " + uuid);
				registrationLatch.countDown();
			});

			RegisterRequest req = new RegisterRequest(agent.getUid(), "test-agent", agent.getName(), "A Java based test agent", false);
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

			// at the end of registration process, agent UUID must be set
			assertNotNull(agent.getUuid());
		}
	}

	public static void main(String[] args) throws IOException, InterruptedException, MqttException {
		new MqttAgentTest().register();
	}

}
