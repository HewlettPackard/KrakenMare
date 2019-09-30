package com.hpe.krakenmare.impl;

import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.UUID;

import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.RegisterResponse;

public class MqttRegistrationListener implements IMqttMessageListener {

	public final static Logger LOG = LoggerFactory.getLogger(MqttRegistrationListener.class);

	public static void registerNew(FrameworkMqttListener listener, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getRegistrationRequestTopic(), new MqttRegistrationListener(agentRepo, listener.getClient()));
	}

	private final Repository<Agent> repository;
	private final IMqttClient mqtt;

	public MqttRegistrationListener(Repository<Agent> repository, IMqttClient mqtt) {
		this.repository = repository;
		this.mqtt = mqtt;
	}

	@Override
	public void messageArrived(String topic, MqttMessage message) throws Exception {
		LOG.info("Message received on topic '" + topic + "': " + message);
		RegisterRequest request = RegisterRequest.fromByteBuffer(ByteBuffer.wrap(message.getPayload()));

		String name = request.getName().toString();
		String uid = request.getAgentID().toString();
		Agent agent = new Agent(-1l, uid, null, name);
		agent = registerNewAgent(agent);
		UUID uuid = agent.getUuid();

		RegisterResponse resp = new RegisterResponse(uid, true, "Registration succeed", uuid, Collections.emptyMap());
		byte[] payload = resp.toByteBuffer().array();

		String respTopic = MqttUtils.getRegistrationResponseTopic(agent);
		MqttMessage mqttResponse = new MqttMessage(payload);
		LOG.info("Sending message to topic '" + respTopic + "': " + mqttResponse);
		mqtt.publish(respTopic, mqttResponse);
	}

	private Agent registerNewAgent(Agent agent) {
		agent = repository.create(agent);
		repository.save(agent);
		LOG.info("New agent registered: '" + agent.getName() + "', '" + agent.getUuid() + "'");
		return agent;
	}

}
