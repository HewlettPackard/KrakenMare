package com.hpe.krakenmare.agent;

import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import java.io.IOException;
import java.security.GeneralSecurityException;

import org.apache.kafka.clients.producer.Producer;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.core.Device;
import com.hpe.krakenmare.core.Sensor;
import com.hpe.krakenmare.impl.FrameworkMqttClient;
import com.hpe.krakenmare.impl.KafkaUtils;
import com.hpe.krakenmare.impl.MqttDeviceListListener;
import com.hpe.krakenmare.impl.MqttRegistrationListener;
import com.hpe.krakenmare.impl.MqttUtils;
import com.hpe.krakenmare.repositories.AgentMemoryRepository;

public class MqttAgentTest {

	public final static Logger LOG = LoggerFactory.getLogger(MqttAgentTest.class);

	static String broker = MqttUtils.getBroker();

	@BeforeEach
	public void setup() throws MqttException, GeneralSecurityException {
		FrameworkMqttClient listener = new FrameworkMqttClient();
		listener.start();

		Producer<String, byte[]> kafkaProducer = KafkaUtils.createByteArrayProducer("framework-manager");

		AgentMemoryRepository agents = new AgentMemoryRepository();
		MqttRegistrationListener.registerNew(listener, kafkaProducer, agents);
		MqttDeviceListListener.registerNew(listener, kafkaProducer, agents);
	}

	@Test
	public void registerAgent() throws IOException, InterruptedException, MqttException, GeneralSecurityException {
		MqttAgent agent = new MqttAgent();
		agent.register(broker);
		// at the end of registration process, agent UUID must be set
		assertNotNull(agent.getUuid());

		agent.registerDevices(broker);
		for (Device device : agent.getDevices()) {
			assertNotEquals(MqttUtils.EMPTY_UUID, device.getUuid());
			for (Sensor sensor : device.getSensors()) {
				assertNotEquals(MqttUtils.EMPTY_UUID, sensor.getUuid());
			}
		}
	}

	public static void main(String[] args) throws IOException, InterruptedException, MqttException, GeneralSecurityException {
		new MqttAgent().register(broker);
	}

}
