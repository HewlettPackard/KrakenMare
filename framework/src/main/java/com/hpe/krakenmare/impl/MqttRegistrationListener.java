package com.hpe.krakenmare.impl;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Arrays;
import java.util.Collections;
import java.util.UUID;

import org.apache.avro.util.Utf8;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.message.agent.RegisterRequest;
import com.hpe.krakenmare.message.manager.RegisterResponse;

import io.confluent.kafka.serializers.KafkaAvroSerializer;

public class MqttRegistrationListener extends FrameworkMqttListener<RegisterRequest, RegisterResponse> {

	public final static Logger LOG = LoggerFactory.getLogger(MqttRegistrationListener.class);

	public static void registerNew(FrameworkMqttClient listener, Producer<String, RegisterResponse> kafkaProducer, Repository<Agent> agentRepo) throws MqttException {
		listener.addSubscriber(MqttUtils.getRegistrationRequestTopic(), new MqttRegistrationListener(agentRepo, listener.getClient(), kafkaProducer));
	}

	public MqttRegistrationListener(Repository<Agent> repository, IMqttAsyncClient mqtt, Producer<String, RegisterResponse> kafkaProducer) {
		super(repository, mqtt, kafkaProducer);
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
		String uid = payload.getUid().toString();
		Agent agent = new Agent(-1l, new Utf8(uid), null, new Utf8(name), Collections.emptyList());
		agent = registerNewAgent(agent);
		UUID uuid = agent.getUuid();
		return new RegisterResponse(new Utf8(uid), true, new Utf8("Registration succeed"), uuid, Collections.emptyMap());
	}

	@Override
	void afterProcess(RegisterRequest payload, RegisterResponse response) throws Exception {
		// TODO: we can likely factorize this serialization into super class FrameworkMqttListener
		byte[] respPayload = response.toByteBuffer().array();
		MqttMessage mqttResponse = new MqttMessage(respPayload);
		String respTopic = MqttUtils.getRegistrationResponseTopic(response.getUid());

		System.out.println(Arrays.toString(respPayload));
		KafkaAvroSerializer ser = KafkaUtils.getAvroValueSerializer();
		respPayload = ser.serialize(KafkaUtils.AGENT_REGISTRATION_TOPIC, response);
		System.out.println(Arrays.toString(respPayload));

		LOG.debug("Sending MQTT message to topic '" + respTopic + "': " + mqttResponse);
		mqtt.publish(respTopic, mqttResponse, mqttResponse, new PublishCallback());

		LOG.debug("Sending Kafka message to topic '" + KafkaUtils.AGENT_REGISTRATION_TOPIC + "': " + respPayload);
		ProducerRecord<String, RegisterResponse> record = new ProducerRecord<>(KafkaUtils.AGENT_REGISTRATION_TOPIC, response);
		kafkaProducer.send(record);
	}

}
