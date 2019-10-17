package com.hpe.krakenmare.agent;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.io.IOException;

import org.eclipse.paho.client.mqttv3.MqttException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.impl.FrameworkMqttClient;
import com.hpe.krakenmare.impl.MqttRegistrationListener;
import com.hpe.krakenmare.impl.MqttSensorListListener;
import com.hpe.krakenmare.repositories.AgentMemoryRepository;

public class MqttAgentTest {

	public final static Logger LOG = LoggerFactory.getLogger(MqttAgentTest.class);

	static String broker = "tcp://" + Main.getProperty("mqtt.server"); // "tcp://mosquitto:1883";

	@BeforeEach
	public void setup() throws MqttException {
		FrameworkMqttClient listener = new FrameworkMqttClient();
		listener.start();

		AgentMemoryRepository agents = new AgentMemoryRepository();
		MqttRegistrationListener.registerNew(listener, agents);
		MqttSensorListListener.registerNew(listener, agents);
	}

	@Test
	public void registerAgent() throws IOException, InterruptedException, MqttException {
		MqttAgent agent = new MqttAgent();
		agent.register(broker);
		// at the end of registration process, agent UUID must be set
		assertNotNull(agent.getUuid());

		agent.registerDevices(broker);
	}

	public static void main(String[] args) throws IOException, InterruptedException, MqttException {
		new MqttAgent().register(broker);
	}

}
