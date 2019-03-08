package com.hpe.pathforward.agent;

import java.time.Duration;
import java.util.Collections;

import org.apache.kafka.clients.consumer.Consumer;
import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.pathforward.framework.Framework;

public class AgentClient {

	public final static Logger LOG = LoggerFactory.getLogger(AgentClient.class);

	private static Producer<String, String> createProducer() {
		Framework.PROPERTIES.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		Framework.PROPERTIES.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		return new KafkaProducer<>(Framework.PROPERTIES);
	}

	private static Consumer<String, Agent> createConsumer() {
		Framework.PROPERTIES.put(ConsumerConfig.GROUP_ID_CONFIG, "AgentConsumer");
		Framework.PROPERTIES.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		Framework.PROPERTIES.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		return new KafkaConsumer<>(Framework.PROPERTIES);
	}

	static void startAgentRegistrationConsumer() {
		Thread t = new Thread(() -> {
			try (Consumer<String, Agent> consumer = createConsumer()) {
				String topic = Framework.PROPERTIES.getProperty("pf.registration.result-topic");
				consumer.subscribe(Collections.singletonList(topic));

				final ConsumerRecords<String, Agent> consumerRecords = consumer.poll(Duration.ofSeconds(30));

				consumerRecords.forEach(record -> {
					LOG.info("Consumer Record: {}", record.value());
				});
			}
		});
		t.start();
	}

	static void sendAgentRegistrationMessage() throws Exception {
		try (Producer<String, String> producer = createProducer()) {
			String topic = Framework.PROPERTIES.getProperty("pf.registration.request-topic");
			final ProducerRecord<String, String> record = new ProducerRecord<>(topic, "myAgentName");
			/* RecordMetadata metadata = */ producer.send(record).get();

			LOG.info("Producer Record: {}", record.value());
		}
	}

	public static void main(String[] args) throws Exception {
		startAgentRegistrationConsumer();
		sendAgentRegistrationMessage();
	}

}
