package com.hpe.krakenmare.impl;

import java.util.UUID;

import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
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

	// TODO: error handling (agent not found...)
	// TODO: atomicity? repo.delete(UUID)?
	private boolean deregisterAgent(UUID agentUuid) throws EntityNotFoundException {
		Agent agent = repository.get(agentUuid);
		return repository.delete(agent);
	}

	@Override
	DeregisterResponse process(DeregisterRequest payload) throws EntityNotFoundException {
		UUID uuid = payload.getUuid();
		boolean success = deregisterAgent(uuid);
		if (success) {
			LOG.info("Agent deregistered: " + uuid);
		} else {
			LOG.warn("Unable to deleted agent: " + uuid);
		}
		return new DeregisterResponse(uuid, success);
	}

	@Override
	void afterProcess(DeregisterRequest payload, DeregisterResponse response) throws Exception {
		// TODO: we can likely factorize this serialization into super class FrameworkMqttListener
		byte[] respPayload = serializer.serialize(KafkaUtils.AGENT_DEREGISTRATION_TOPIC, response);
		MqttMessage mqttResponse = new MqttMessage(respPayload);
		mqttResponse.setQos(MqttUtils.getPublishQos());
		String respTopic = MqttUtils.getDeregistrationResponseTopic(response.getAgentUuid());

		// LOG.debug("Sending MQTT message to topic '" + respTopic + "': " + mqttResponse);
		LOG.debug("Sending MQTT message to topic '" + respTopic + "'");
		mqtt.publish(respTopic, mqttResponse, mqttResponse, new PublishCallback());

		// LOG.debug("Sending Kafka message to topic '" + KafkaUtils.AGENT_DEREGISTRATION_TOPIC + "': " + respPayload);
		LOG.debug("Sending Kafka message to topic '" + KafkaUtils.AGENT_DEREGISTRATION_TOPIC + "'");
		ProducerRecord<String, byte[]> record = new ProducerRecord<>(KafkaUtils.AGENT_DEREGISTRATION_TOPIC, payload.getUuid().toString(), respPayload);
		kafkaProducer.send(record);
	}

}
