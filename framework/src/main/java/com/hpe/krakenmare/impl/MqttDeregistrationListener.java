/**
 * (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
 */
package com.hpe.krakenmare.impl;

import java.util.UUID;

import org.apache.kafka.clients.producer.Producer;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.EntityNotFoundException;
import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.message.agent.DeregisterRequest;
import com.hpe.krakenmare.message.manager.DeregisterResponse;

public class MqttDeregistrationListener extends FrameworkMqttListener<DeregisterRequest, DeregisterResponse> {

	public final static Logger LOG = LoggerFactory.getLogger(MqttDeregistrationListener.class);

	public static void registerNew(FrameworkMqttClient listener, Producer<String, byte[]> kafkaProducer, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getDeregistrationRequestTopic(), new MqttDeregistrationListener(agentRepo, listener.getClient(), kafkaProducer));
	}

	public MqttDeregistrationListener(Repository<Agent> repository, IMqttAsyncClient mqtt, Producer<String, byte[]> kafkaProducer) {
		super(repository, mqtt, kafkaProducer);
	}

	// TODO: atomicity? repo.delete(UUID)?
	private boolean deregisterAgent(UUID agentUuid) throws EntityNotFoundException {
		Agent agent = repository.get(agentUuid);
		return repository.delete(agent);
	}

	@Override
	DeregisterResponse process(DeregisterRequest payload) throws EntityNotFoundException, MqttException {
		UUID uuid = payload.getUuid();
		boolean success = deregisterAgent(uuid);
		if (success) {
			LOG.info("Agent deregistered: " + uuid);
		} else {
			LOG.warn("Unable to deleted agent: " + uuid);
		}

		String topic = MqttUtils.getDeregistrationResponseTopic(payload.getUuid());
		DeregisterResponse response = new DeregisterResponse(uuid, success);
		sendMqttResponse(topic, response);

		sendKafkaMessage(KafkaUtils.AGENT_DEREGISTRATION_TOPIC, uuid, response);

		return response;
	}

}
