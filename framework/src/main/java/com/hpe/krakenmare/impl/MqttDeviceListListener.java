package com.hpe.krakenmare.impl;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.apache.avro.util.Utf8;
import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.core.Device;
import com.hpe.krakenmare.core.Sensor;
import com.hpe.krakenmare.message.agent.DeviceList;
import com.hpe.krakenmare.message.manager.DeviceListResponse;
import com.hpe.krakenmare.message.manager.SensorUuids;

public class MqttDeviceListListener extends FrameworkMqttListener<DeviceList, DeviceListResponse> {

	public final static Logger LOG = LoggerFactory.getLogger(MqttDeviceListListener.class);

	public static void registerNew(FrameworkMqttClient listener, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getSensorListRequestTopic(), new MqttDeviceListListener(agentRepo, listener.getClient()));
	}

	public MqttDeviceListListener(Repository<Agent> repository, IMqttClient mqtt) {
		super(repository, mqtt);
	}

	@Override
	DeviceList fromByteBuffer(ByteBuffer b) throws IOException {
		return DeviceList.fromByteBuffer(b);
	}

	@Override
	DeviceListResponse process(DeviceList sensorList) {
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
		repository.save(agent);

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
	void afterProcess(DeviceList payload, DeviceListResponse response) throws IOException, MqttPersistenceException, MqttException {
		// TODO: we can likely factorize this serialization into super class FrameworkMqttListener
		byte[] respPayload = response.toByteBuffer().array();
		MqttMessage mqttResponse = new MqttMessage(respPayload);
		String respTopic = MqttUtils.getSensorListResponseTopic(response.getUuid());

		LOG.info("Sending message to topic '" + respTopic + "': " + mqttResponse);
		mqtt.publish(respTopic, mqttResponse);
	}

}
