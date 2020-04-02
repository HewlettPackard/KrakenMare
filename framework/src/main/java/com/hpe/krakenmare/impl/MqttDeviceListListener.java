package com.hpe.krakenmare.impl;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.apache.avro.util.Utf8;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.EntityNotFoundException;
import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.core.Device;
import com.hpe.krakenmare.core.Sensor;
import com.hpe.krakenmare.message.agent.DeviceList;
import com.hpe.krakenmare.message.manager.DeviceListResponse;
import com.hpe.krakenmare.message.manager.SensorUuids;

public class MqttDeviceListListener extends FrameworkMqttListener<DeviceList, DeviceListResponse> {

	public final static Logger LOG = LoggerFactory.getLogger(MqttDeviceListListener.class);

	public static void registerNew(FrameworkMqttClient listener, Producer<String, byte[]> kafkaProducer, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getSensorListRequestTopic(), new MqttDeviceListListener(agentRepo, listener.getClient(), kafkaProducer));
	}

	public MqttDeviceListListener(Repository<Agent> repository, IMqttAsyncClient mqtt, Producer<String, byte[]> kafkaProducer) {
		super(repository, mqtt, kafkaProducer);
	}

	@Override
	DeviceListResponse process(DeviceList sensorList) throws EntityNotFoundException {
		UUID agentUuid = sensorList.getUuid();
		List<Device> devices = sensorList.getDevices();

		for (Device device : devices) {
			device.setUuid(UUID.randomUUID());
			for (Sensor sensor : device.getSensors()) {
				sensor.setUuid(UUID.randomUUID());
			}
		}

		Agent agent = repository.get(agentUuid);
		agent.setDevices(devices);
		repository.update(agent);

		Map<Utf8, SensorUuids> uuids = new HashMap<>();
		devices.forEach(d -> {
			Map<Utf8, UUID> sensorUuidsMap = new HashMap<>();
			d.getSensors().forEach(s -> sensorUuidsMap.put(s.getId(), s.getUuid()));
			SensorUuids sensorUuids = new SensorUuids(d.getUuid(), sensorUuidsMap);
			uuids.put(d.getId(), sensorUuids);
		});

		return new DeviceListResponse(agentUuid, uuids);
	}

	@Override
	String getMqttResponseTopic(DeviceList payload) {
		return MqttUtils.getSensorListResponseTopic(payload.getUuid());
	}

	@Override
	protected void afterProcess(DeviceList payload, DeviceListResponse response) throws MqttPersistenceException, MqttException {
		super.afterProcess(payload, response);

		// LOG.debug("Sending Kafka message to topic '" + KafkaUtils.DEVICE_REGISTRATION_TOPIC + "': " + respPayload);
		LOG.debug("Sending Kafka message to topic '" + KafkaUtils.DEVICE_REGISTRATION_TOPIC + "'");
		byte[] respPayload = serializer.serialize(null, response);
		ProducerRecord<String, byte[]> record = new ProducerRecord<>(KafkaUtils.DEVICE_REGISTRATION_TOPIC, payload.getUuid().toString(), respPayload);
		kafkaProducer.send(record);
	}

}
