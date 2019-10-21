package com.hpe.krakenmare.agent;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import org.apache.avro.util.Utf8;
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
import com.hpe.krakenmare.message.manager.SensorUuids;

public class MqttAgent extends Agent {

	public final static Logger LOG = LoggerFactory.getLogger(MqttAgent.class);

	private final static String NAME = MqttAgent.class.getSimpleName();

	public MqttAgent() {
		super(-1l,
				new Utf8(NAME + "-" + System.currentTimeMillis()),
				null,
				new Utf8(NAME),
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

			RegisterRequest req = new RegisterRequest(getUid(), new Utf8("test-agent"), getName(), new Utf8("A Java based test agent"), false);
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

				try {
					for (Device device : getDevices()) {
						SensorUuids uuids = response.getDeviceUuids().get(device.getId());
						device.setUuid(uuids.getUuid());
						for (Sensor sensor : device.getSensors()) {
							sensor.setUuid(uuids.getSensorUuids().get(sensor.getId()));
						}
					}
				} catch (Exception e) {
					LOG.error("Error while registering devices", e);
				} finally {
					registrationLatch.countDown();
				}
			});

			Sensor sensor = new Sensor(MqttUtils.EMPTY_UUID,
					new Utf8("mySensor-1"),
					new Utf8("mySensor"),
					Collections.emptyMap(), // collectionFrequency,
					new Utf8(), // measuringAccuracy,
					new Utf8(), // unit,
					new Utf8(), // type,
					Collections.emptyMap(), // valueRange,
					42f, // changeFrequency,
					42f, // currentCollectionFrequency,
					42); // , storageTime);
			List<Sensor> sensors = new ArrayList<>();
			sensors.add(sensor);

			Device device = new Device(MqttUtils.EMPTY_UUID,
					new Utf8("myDevice-1"),
					new Utf8("myDevice"),
					new Utf8("test-device"),
					new Utf8("somewhere"),
					sensors);
			List<Device> devices = new ArrayList<>();
			devices.add(device);
			setDevices(devices);

			SensorList req = new SensorList(getUuid(), getDevices());
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
