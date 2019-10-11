package com.hpe.krakenmare.impl;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.UUID;

import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.RegisterResponse;

public class MqttRegistrationListener extends FrameworkMqttListener<RegisterRequest, RegisterResponse> {

	public final static Logger LOG = LoggerFactory.getLogger(MqttRegistrationListener.class);

	public static void registerNew(FrameworkMqttClient listener, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getRegistrationRequestTopic(), new MqttRegistrationListener(agentRepo, listener.getClient()));
	}

	public MqttRegistrationListener(Repository<Agent> repository, IMqttClient mqtt) {
		super(repository, mqtt);
	}

	private Agent registerNewAgent(Agent agent) {
		agent = repository.create(agent);
		repository.save(agent);
		LOG.info("New agent registered: '" + agent.getName() + "', '" + agent.getUuid() + "'");
		return agent;
	}

	@Override
	RegisterRequest fromByteBuffer(ByteBuffer b) throws IOException {
		return RegisterRequest.fromByteBuffer(b);
	}

	@Override
	RegisterResponse process(RegisterRequest payload) {
		String name = payload.getName().toString();
		String uid = payload.getAgentID().toString();
		Agent agent = new Agent(-1l, uid, null, name, Collections.emptyList());
		agent = registerNewAgent(agent);
		UUID uuid = agent.getUuid();
		return new RegisterResponse(uid, true, "Registration succeed", uuid, Collections.emptyMap());
	}

	@Override
	void afterProcess(RegisterRequest payload, RegisterResponse response) throws Exception {
		// TODO: we can likely factorize this serialization into super class FrameworkMqttListener
		byte[] respPayload = response.toByteBuffer().array();
		MqttMessage mqttResponse = new MqttMessage(respPayload);
		String respTopic = MqttUtils.getRegistrationResponseTopic(response.getAgentID());

		LOG.info("Sending message to topic '" + respTopic + "': " + mqttResponse);
		mqtt.publish(respTopic, mqttResponse);
	}

}
