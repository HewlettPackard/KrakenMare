package com.hpe.krakenmare.impl;

import org.apache.avro.specific.SpecificRecordBase;
import org.apache.kafka.clients.producer.Producer;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;

import io.confluent.kafka.serializers.KafkaAvroDeserializer;
import io.confluent.kafka.serializers.KafkaAvroSerializer;

public abstract class FrameworkMqttListener<P extends SpecificRecordBase, R extends SpecificRecordBase> implements IMqttMessageListener {

	final static Logger LOG = LoggerFactory.getLogger(FrameworkMqttListener.class);

	protected final Repository<Agent> repository;
	protected final IMqttAsyncClient mqtt;
	protected final Producer<String, byte[]> kafkaProducer;
	protected final KafkaAvroSerializer serializer = KafkaUtils.getAvroValueSerializer();
	protected final KafkaAvroDeserializer deserializer = KafkaUtils.getAvroValueDeserializer();

	public FrameworkMqttListener(Repository<Agent> repository, IMqttAsyncClient mqtt, Producer<String, byte[]> kafkaProducer) {
		this.repository = repository;
		this.mqtt = mqtt;
		this.kafkaProducer = kafkaProducer;
	}

	@Override
	public void messageArrived(String topic, MqttMessage message) {
		LOG.info("Message received on topic '" + topic + "': " + message);
		try {
			@SuppressWarnings("unchecked")
			P payload = (P) deserializer.deserialize(null /* ignored */, message.getPayload());
			R response = process(payload);
			afterProcess(payload, response);
		} catch (Exception e) {
			LOG.error("Exception occured during message handling", e);
		}
	}

	abstract R process(P payload);

	abstract void afterProcess(P payload, R response) throws Exception;

	// uses the userContext to carry the MqttMessage sent
	static class PublishCallback implements IMqttActionListener {

		@Override
		public void onSuccess(IMqttToken asyncActionToken) {
			String topic = asyncActionToken.getTopics()[0];
			int messageId = asyncActionToken.getMessageId();
			Object message = asyncActionToken.getUserContext();
			LOG.info("Message successfully sent to topic '" + topic + "': " + message + " (id=" + messageId + ")");
		}

		@Override
		public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
			String topic = asyncActionToken.getTopics()[0];
			int messageId = asyncActionToken.getMessageId();
			Object message = asyncActionToken.getUserContext();
			LOG.error("Failed to send message to topic '" + topic + "': " + message + " (id=" + messageId + ")", exception);
		}

	}

}
