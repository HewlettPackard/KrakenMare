package com.hpe.krakenmare.agent;

import java.io.IOException;
import java.security.GeneralSecurityException;
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
import com.hpe.krakenmare.impl.KafkaUtils;
import com.hpe.krakenmare.impl.MqttUtils;
import com.hpe.krakenmare.message.agent.DeregisterRequest;
import com.hpe.krakenmare.message.agent.DeviceList;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.DeregisterResponse;
import com.hpe.krakenmare.message.manager.DeviceListResponse;
import com.hpe.krakenmare.message.manager.RegisterResponse;
import com.hpe.krakenmare.message.manager.SensorUuids;

import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroSerializer;

public class MqttAgent extends Agent {

	public final static Logger LOG = LoggerFactory.getLogger(MqttAgent.class);

	private final static String NAME = MqttAgent.class.getSimpleName();

	private final KafkaAvroSerializer avroSer = KafkaUtils.getAvroValueSerializer();
	private final KafkaAvroDeserializer avroDes = KafkaUtils.getAvroValueDeserializer();

	public MqttAgent() {
		super(-1l,
				new Utf8(NAME + "-" + System.currentTimeMillis()),
				null,
				new Utf8(NAME),
				Collections.emptyList());
	}

	// TODO: open a long living MQTT connection to "MY-UUID/+" to receive all messages, then process them base on topic name
	public void register(String broker) throws IOException, InterruptedException, MqttException, GeneralSecurityException {
		String myAgentTopic = MqttUtils.getRegistrationRequestTopic(this);
		String myManagerTopic = MqttUtils.getRegistrationResponseTopic(this);

		try (MqttClient mqtt = new MqttClient(broker, getUid().toString(), new MemoryPersistence())) {
			LOG.info("Connecting to broker: " + broker);
			MqttConnectOptions connOpts = MqttUtils.getConnectOptions();
			mqtt.connect(connOpts);
			LOG.info("Connected");

			CountDownLatch registrationLatch = new CountDownLatch(1);
			mqtt.subscribe(myManagerTopic, (topic, message) -> {
				LOG.info("Message received on topic '" + topic + "': " + message);
				RegisterResponse response = (RegisterResponse) avroDes.deserialize(null /* ignored */, message.getPayload());
				UUID uuid = response.getUuid();
				setUuid(uuid);
				LOG.info("UUID received from manager: " + uuid);
				registrationLatch.countDown();
			});

			RegisterRequest req = new RegisterRequest(getUid(), new Utf8("test-agent"), getName(), new Utf8("A Java based test agent"), false);
			byte[] payload = avroSer.serialize(KafkaUtils.AGENT_REGISTRATION_TOPIC, req);

			LOG.info("Publishing message '" + req + "' to topic '" + myAgentTopic + "'");
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

	public void registerDevices(String broker) throws MqttException, IOException, InterruptedException, GeneralSecurityException {
		String myAgentTopic = MqttUtils.getSensorListRequestTopic(this);
		String myManagerTopic = MqttUtils.getSensorListResponseTopic(this);

		try (MqttClient mqtt = new MqttClient(broker, getUid().toString(), new MemoryPersistence())) {
			LOG.info("Connecting to broker: " + broker);
			MqttConnectOptions connOpts = MqttUtils.getConnectOptions();
			mqtt.connect(connOpts);
			LOG.info("Connected");

			CountDownLatch registrationLatch = new CountDownLatch(1);
			mqtt.subscribe(myManagerTopic, (topic, message) -> {
				LOG.info("Message received on topic '" + topic + "': " + message);
				DeviceListResponse response = (DeviceListResponse) avroDes.deserialize(null /* ignored */, message.getPayload());
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

			Sensor sensor = new Sensor(MqttUtils.EMPTY_UUID, // uuid
					new Utf8("mySensor-1"), // id
					new Utf8("mySensor"), // name
					42f, // collectionFrequencyMin
					42f, // collectionFrequencyMax
					42f, // collectionFrequencyDefault
					new Utf8(), // measuringAccuracy,
					new Utf8(), // unit,
					new Utf8(), // type,
					42f, // valueRangeMin
					42f, // valueRangeMax
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

			DeviceList req = new DeviceList(getUuid(), getDevices());
			byte[] payload = avroSer.serialize(KafkaUtils.DEVICE_REGISTRATION_TOPIC, req);

			LOG.info("Publishing message '" + req + "' to topic '" + myAgentTopic + "'");
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

	public void deregister(String broker) throws IOException, InterruptedException, MqttException, GeneralSecurityException {
		String myAgentTopic = MqttUtils.getDeregistrationRequestTopic(this);
		String myManagerTopic = MqttUtils.getDeregistrationResponseTopic(this);

		try (MqttClient mqtt = new MqttClient(broker, getUid().toString(), new MemoryPersistence())) {
			LOG.info("Connecting to broker: " + broker);
			MqttConnectOptions connOpts = MqttUtils.getConnectOptions();
			mqtt.connect(connOpts);
			LOG.info("Connected");

			CountDownLatch registrationLatch = new CountDownLatch(1);
			mqtt.subscribe(myManagerTopic, (topic, message) -> {
				LOG.info("Message received on topic '" + topic + "': " + message);
				DeregisterResponse response = (DeregisterResponse) avroDes.deserialize(null /* ignored */, message.getPayload());
				boolean success = response.getSuccess();
				LOG.info("Deregistration " + (success ? "succeed" : "failed"));
				registrationLatch.countDown();
			});

			DeregisterRequest req = new DeregisterRequest(getUuid());
			byte[] payload = avroSer.serialize(KafkaUtils.AGENT_DEREGISTRATION_TOPIC, req);

			LOG.info("Publishing message '" + req + "' to topic '" + myAgentTopic + "'");
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
