package com.hpe.krakenmare.impl;

import java.util.Collections;
import java.util.UUID;

import org.apache.avro.util.Utf8;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.RegisterResponse;

public class MqttRegistrationListener extends FrameworkMqttListener<RegisterRequest, RegisterResponse> {

	public final static Logger LOG = LoggerFactory.getLogger(MqttRegistrationListener.class);

	public static void registerNew(FrameworkMqttClient listener, Producer<String, byte[]> kafkaProducer, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getRegistrationRequestTopic(), new MqttRegistrationListener(agentRepo, listener.getClient(), kafkaProducer));
	}

	public MqttRegistrationListener(Repository<Agent> repository, IMqttAsyncClient mqtt, Producer<String, byte[]> kafkaProducer) {
		super(repository, mqtt, kafkaProducer);
	}

	private Agent registerNewAgent(Agent agent) {
		agent = repository.create(agent);
		repository.save(agent);
		LOG.info("New agent registered: '" + agent.getName() + "', '" + agent.getId() + "', '" + agent.getUuid() + "'");
		return agent;
	}

	@Override
	RegisterResponse process(RegisterRequest payload) throws MqttPersistenceException, MqttException {
		String name = payload.getName().toString();
		String uid = payload.getUid().toString();
		Agent agent = new Agent(-1l, new Utf8(uid), null, new Utf8(name), Collections.emptyList());
		agent = registerNewAgent(agent);
		UUID uuid = agent.getUuid();

		String topic = MqttUtils.getRegistrationResponseTopic(payload.getUid());
		RegisterResponse response = new RegisterResponse(new Utf8(uid), true, new Utf8("Registration succeed"), uuid, Collections.emptyMap());
		sendMqttResponse(topic, response);

		// LOG.debug("Sending Kafka message to topic '" + KafkaUtils.AGENT_REGISTRATION_TOPIC + "': " + respPayload);
		LOG.debug("Sending Kafka message to topic '" + KafkaUtils.AGENT_REGISTRATION_TOPIC + "'");
		byte[] respPayload = serializer.serialize(null, response);
		ProducerRecord<String, byte[]> record = new ProducerRecord<>(KafkaUtils.AGENT_REGISTRATION_TOPIC, response.getUuid().toString(), respPayload);
		kafkaProducer.send(record);

		return response;
	}

}
