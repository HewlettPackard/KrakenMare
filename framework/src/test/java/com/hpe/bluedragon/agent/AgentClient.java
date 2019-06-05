package com.hpe.bluedragon.agent;

import java.time.Duration;
import java.util.Collections;
import java.util.Properties;

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

import com.hpe.bluedragon.Main;
import com.hpe.bluedragon.core.Agent;

public class AgentClient {

	private final static Logger LOG = LoggerFactory.getLogger(AgentClient.class);
	private final static Properties PROPERTIES = Main.cloneProperties();

	private static Producer<String, String> createProducer() {
		PROPERTIES.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		PROPERTIES.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		return new KafkaProducer<>(PROPERTIES);
	}

	private static Consumer<String, Agent> createConsumer() {
		PROPERTIES.put(ConsumerConfig.GROUP_ID_CONFIG, "AgentConsumer");
		PROPERTIES.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		PROPERTIES.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
		return new KafkaConsumer<>(PROPERTIES);
	}

	static void startAgentRegistrationConsumer() {
		Thread t = new Thread(() -> {
			try (Consumer<String, Agent> consumer = createConsumer()) {
				String topic = PROPERTIES.getProperty("bd.registration.result-topic");
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
			String topic = PROPERTIES.getProperty("bd.registration.request-topic");
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
