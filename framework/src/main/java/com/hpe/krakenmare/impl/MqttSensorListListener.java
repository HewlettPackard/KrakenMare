package com.hpe.krakenmare.impl;

import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.core.Device;
import com.hpe.krakenmare.message.agent.SensorList;
import com.hpe.krakenmare.message.manager.SensorListResponse;
import com.hpe.krakenmare.message.manager.SensorUuids;

public class MqttSensorListListener implements IMqttMessageListener {

	public final static Logger LOG = LoggerFactory.getLogger(MqttSensorListListener.class);

	public static void registerNew(FrameworkMqttListener listener, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getSensorListRequestTopic(), new MqttSensorListListener(agentRepo, listener.getClient()));
	}

	private final Repository<Agent> repository;
	private final IMqttClient mqtt;

	public MqttSensorListListener(Repository<Agent> repository, IMqttClient mqtt) {
		this.repository = repository;
		this.mqtt = mqtt;
	}

	@Override
	public void messageArrived(String topic, MqttMessage message) {
		LOG.info("Message received on topic '" + topic + "': " + message);
		try {
			SensorList sensorList = SensorList.fromByteBuffer(ByteBuffer.wrap(message.getPayload()));
			SensorListResponse resp = process(sensorList);

			String respTopic = MqttUtils.getSensorListResponseTopic(resp.getUuid());
			byte[] payload = resp.toByteBuffer().array();

			MqttMessage mqttResponse = new MqttMessage(payload);
			LOG.info("Sending message to topic '" + respTopic + "': " + mqttResponse);
			mqtt.publish(respTopic, mqttResponse);
		} catch (Exception e) {
			LOG.error("Exception occured during message handling", e);
		}
	}

	private SensorListResponse process(SensorList sensorList) {
		UUID agentUuid = sensorList.getUuid();
		List<Device> devices = sensorList.getDevices();

		Agent agent = repository.get(agentUuid);
		agent.setDevices(devices);
		repository.save(agent);

		Map<CharSequence, SensorUuids> uuids = new HashMap<>();
		devices.forEach(d -> {
			Map<CharSequence, UUID> sensorUuidsMap = new HashMap<>();
			d.getSensors().forEach(s -> sensorUuidsMap.put(s.getId(), s.getUuid()));
			SensorUuids sensorUuids = new SensorUuids(d.getUuid(), sensorUuidsMap);
			uuids.put(d.getId(), sensorUuids);
		});

		return new SensorListResponse(agentUuid, uuids);
	}

}
