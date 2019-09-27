package com.hpe.krakenmare.agent;

import java.io.IOException;

import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.impl.FrameworkMqttListener;
import com.hpe.krakenmare.impl.MqttRegistrationListener;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.repositories.AgentRepository;

public class MqttAgentTest {

	static String broker = "tcp://" + Main.getProperty("mqtt.server"); // "tcp://mosquitto:1883";
	static String registrationRequestTopic = Main.getProperty("km.registration.mqtt.topic");

	static int qos = 2;

	private final long myId = System.currentTimeMillis();

	@BeforeEach
	public void setup() throws MqttException {
		FrameworkMqttListener listener = new FrameworkMqttListener();
		listener.start();

		AgentRepository agents = new AgentRepository();
		listener.addSubscriber(registrationRequestTopic + "#", qos, new MqttRegistrationListener(agents, listener.getClient()));
	}

	@Test
	public void register() throws IOException {
		String myTopic = registrationRequestTopic + myId;
		String name = MqttAgentTest.class.getSimpleName();
		String id = name + "-" + myId;

		try (MqttClient sampleClient = new MqttClient(broker, id, new MemoryPersistence())) {
			MqttConnectOptions connOpts = new MqttConnectOptions();
			System.out.println("Connecting to broker: " + broker);
			sampleClient.connect(connOpts);
			System.out.println("Connected");

			RegisterRequest req = new RegisterRequest(id, "test-agent", name, "A Java based test agent", false);
			byte[] payload = req.toByteBuffer().array();

			System.out.println("Publishing message '" + new String(payload) + "' to topic '" + myTopic + "'");
			MqttMessage message = new MqttMessage(payload);
			message.setQos(qos);
			sampleClient.publish(myTopic, message);
			System.out.println("Message published");

			sampleClient.disconnect();
			System.out.println("Disconnected");
		} catch (MqttException me) {
			System.out.println("reason " + me.getReasonCode());
			System.out.println("msg " + me.getMessage());
			System.out.println("loc " + me.getLocalizedMessage());
			System.out.println("cause " + me.getCause());
			System.out.println("excep " + me);
			me.printStackTrace();
		}
	}

}
