package com.hpe.krakenmare.impl;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.UUID;

import org.apache.avro.util.Utf8;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
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

	public MqttRegistrationListener(Repository<Agent> repository, IMqttAsyncClient mqtt) {
		super(repository, mqtt);
	}

	private Agent registerNewAgent(Agent agent) {
		agent = repository.create(agent);
		repository.save(agent);
		LOG.info("New agent registered: '" + agent.getAgentName() + "', '" + agent.getAgentUuid() + "'");
		return agent;
	}

	@Override
	RegisterRequest fromByteBuffer(ByteBuffer b) throws IOException {
		return RegisterRequest.fromByteBuffer(b);
	}

	@Override
	RegisterResponse process(RegisterRequest payload) {
		String name = payload.getAgentName().toString();
		String uid = payload.getAgentId().toString();
		Agent agent = new Agent(-1l, new Utf8(uid), null, new Utf8(name), Collections.emptyList());
		agent = registerNewAgent(agent);
		UUID uuid = agent.getAgentUuid();
		return new RegisterResponse(new Utf8(uid), true, new Utf8("Registration succeed"), uuid, Collections.emptyMap());
	}

	@Override
	void afterProcess(RegisterRequest payload, RegisterResponse response) throws Exception {
		// TODO: we can likely factorize this serialization into super class FrameworkMqttListener
		byte[] respPayload = response.toByteBuffer().array();
		MqttMessage mqttResponse = new MqttMessage(respPayload);
		String respTopic = MqttUtils.getRegistrationResponseTopic(response.getAgentId());

		LOG.debug("Sending message to topic '" + respTopic + "': " + mqttResponse);
		mqtt.publish(respTopic, mqttResponse, mqttResponse, new PublishCallback());
	}

}
