package com.hpe.krakenmare.impl;

import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.UUID;

import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.RegisterResponse;

public class MqttRegistrationListener implements IMqttMessageListener {

	public final static Logger LOG = LoggerFactory.getLogger(MqttRegistrationListener.class);

	private final Repository<Agent> repository;
	private final IMqttClient mqqtClient;
	private final String registrationResultTopic = Main.getProperty("km.registration.mqtt.topic");

	public MqttRegistrationListener(Repository<Agent> repository, IMqttClient mqqtClient) {
		this.repository = repository;
		this.mqqtClient = mqqtClient;
	}

	@Override
	public void messageArrived(String topic, MqttMessage message) throws Exception {
		LOG.info("Message received on topic '" + topic + "': " + message);
		RegisterRequest request = RegisterRequest.fromByteBuffer(ByteBuffer.wrap(message.getPayload()));

		String name = request.getName().toString();
		String id = request.getAgentID().toString();
		Agent agent = registerNewAgent(name);
		UUID uuid = agent.getUuid();

		RegisterResponse resp = new RegisterResponse(id, true, "success", uuid, Collections.emptyMap());
		byte[] payload = resp.toByteBuffer().array();

		MqttMessage mqttResponse = new MqttMessage(payload);
		mqqtClient.publish(registrationResultTopic + "/" + uuid, mqttResponse);
	}

	private Agent registerNewAgent(String name) {
		Agent agent = repository.create(name, UUID.randomUUID());
		repository.save(agent);
		LOG.info("New agent registered: '" + name + "', '" + agent.getUuid() + "'");
		return agent;
	}

}
