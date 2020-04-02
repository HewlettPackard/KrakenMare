package com.hpe.krakenmare.impl;

import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

import org.apache.avro.specific.SpecificRecordBase;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttAsyncClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.FrameworkException;
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

	private final static ExecutorService executor = Executors.newFixedThreadPool(128);
	private final AtomicInteger counter = new AtomicInteger(0);
	private final AtomicLong firstReceived = new AtomicLong(0);

	public FrameworkMqttListener(Repository<Agent> repository, IMqttAsyncClient mqtt, Producer<String, byte[]> kafkaProducer) {
		this.repository = repository;
		this.mqtt = mqtt;
		this.kafkaProducer = kafkaProducer;
	}

	@Override
	public void messageArrived(String topic, MqttMessage message) {
		executor.execute(() -> {
			// LOG.info("Message received on topic '" + topic + "': " + message);
			int c = counter.incrementAndGet();
			long start = System.currentTimeMillis();

			firstReceived.compareAndSet(0, start);
			LOG.info("Message received on topic '" + topic + "' (#" + c + ")");

			try {
				@SuppressWarnings("unchecked")
				P payload = (P) deserializer.deserialize(/* ignored */ null, message.getPayload());
				process(payload);
				long stop = System.currentTimeMillis();
				LOG.info("Message processed on topic '" + topic + "' (#" + c + ", " + (start - firstReceived.get()) + "ms, " + (stop - start) + "ms)");
			} catch (Exception e) {
				LOG.error("Exception occured during message handling (#" + c + ")", e);
			}
		});
	}

	abstract R process(P payload) throws FrameworkException, MqttException;

	protected void sendMqttResponse(String topic, R response) throws MqttPersistenceException, MqttException {
		// we don't care about the Kafka topic (null) because we are using RecordNameStrategy for VALUE_SUBJECT_NAME_STRATEGY
		byte[] respPayload = serializer.serialize(/* ignored */ null, response);
		MqttMessage mqttResponse = new MqttMessage(respPayload);
		mqttResponse.setQos(MqttUtils.getPublishQos());

		LOG.debug("Sending MQTT message to topic '" + topic + "'");
		mqtt.publish(topic, mqttResponse, mqttResponse, new PublishCallback());
	}

	// do not use R type, we want to be able to send anything
	protected void sendKafkaMessage(String topic, UUID key, Object response) {
		LOG.debug("Sending Kafka message to topic '" + topic + "'");
		byte[] respPayload = serializer.serialize(/* ignored */ null, response);
		ProducerRecord<String, byte[]> record = new ProducerRecord<>(topic, (key == null) ? null : key.toString(), respPayload);
		kafkaProducer.send(record);
	}

	// uses the userContext to carry the MqttMessage sent
	static class PublishCallback implements IMqttActionListener {

		@Override
		public void onSuccess(IMqttToken asyncActionToken) {
			String topic = asyncActionToken.getTopics()[0];
			int messageId = asyncActionToken.getMessageId();
			// Object message = asyncActionToken.getUserContext();
			// LOG.info("Message successfully sent to topic '" + topic + "': " + message + " (id=" + messageId + ")");
			LOG.info("Message successfully sent to topic '" + topic + "' (id=" + messageId + ")");
		}

		@Override
		public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
			String topic = asyncActionToken.getTopics()[0];
			int messageId = asyncActionToken.getMessageId();
			// Object message = asyncActionToken.getUserContext();
			// LOG.error("Failed to send message to topic '" + topic + "': " + message + " (id=" + messageId + ")", exception);
			LOG.error("Failed to send message to topic '" + topic + "' (id=" + messageId + ")", exception);
		}

	}

}
