package com.hpe.krakenmare.agent;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
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
import com.hpe.krakenmare.core.Device;
import com.hpe.krakenmare.core.Sensor;
import com.hpe.krakenmare.impl.MqttUtils;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.agent.SensorList;
import com.hpe.krakenmare.message.manager.RegisterResponse;
import com.hpe.krakenmare.message.manager.SensorListResponse;

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

	// TODO: open a long living MQTT connection to "MY-UUID/+" to receive all messages, then process them base on topic name
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
					throw new RuntimeException("No response received");
				}
			} finally {
				mqtt.disconnect();
				LOG.info("Disconnected");
			}
		}
	}

	public void registerDevices(String broker) throws MqttException, IOException, InterruptedException {
		String myAgentTopic = MqttUtils.getSensorListRequestTopic(this);
		String myManagerTopic = MqttUtils.getSensorListResponseTopic(this);

		try (MqttClient mqtt = new MqttClient(broker, getUid().toString(), new MemoryPersistence())) {
			MqttConnectOptions connOpts = new MqttConnectOptions();
			LOG.info("Connecting to broker: " + broker);
			mqtt.connect(connOpts);
			LOG.info("Connected");

			CountDownLatch registrationLatch = new CountDownLatch(1);
			mqtt.subscribe(myManagerTopic, (topic, message) -> {
				LOG.info("Message received on topic '" + topic + "': " + message);
				SensorListResponse response = SensorListResponse.fromByteBuffer(ByteBuffer.wrap(message.getPayload()));
				LOG.info("Devices UUID received from manager: " + response.getDeviceUuids());
				// TODO
				registrationLatch.countDown();
			});

			Sensor sensor = new Sensor(UUID.randomUUID(),
					"mySensor-1",
					"mySensor",
					null, // collectionFrequency,
					null, // measuringAccuracy,
					null, // unit,
					null, // type,
					null, // valueRange,
					42f, // changeFrequency,
					42f, // currentCollectionFrequency,
					42); // , storageTime);
			List<Sensor> sensors = new ArrayList<>();
			sensors.add(sensor);

			Device device = new Device(UUID.randomUUID(),
					"myDevice-1",
					"myDevice",
					"test-device",
					"somewhere",
					Collections.emptyList());
			List<Device> devices = new ArrayList<>();
			devices.add(device);
			SensorList req = new SensorList(getUuid(), devices);
			byte[] payload = req.toByteBuffer().array();

			LOG.info("Publishing message '" + new String(payload) + "' to topic '" + myAgentTopic + "'");
			MqttMessage message = new MqttMessage(payload);
			mqtt.publish(myAgentTopic, message);
			LOG.info("Message published");

			try {
				// await registration response
				if (!registrationLatch.await(5, TimeUnit.SECONDS)) {
					throw new RuntimeException("No response received");
				}
			} finally {
				mqtt.disconnect();
				LOG.info("Disconnected");
			}
		}
	}

}
