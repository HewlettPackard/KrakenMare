package com.hpe.krakenmare.impl;

import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

import org.apache.avro.Schema;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.MockProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.base.Strings;
import com.hpe.krakenmare.Main;

import io.confluent.kafka.serializers.AbstractKafkaAvroSerDeConfig;
import io.confluent.kafka.serializers.KafkaAvroSerializer;
import io.confluent.kafka.serializers.subject.RecordNameStrategy;

public class KafkaUtils {

	public final static Logger LOG = LoggerFactory.getLogger(KafkaUtils.class);

	public static final String BOOTSTRAP_SERVERS = Main.getProperty("bootstrap.servers");
	public static final String SCHEMA_REGISTRY = Main.getProperty("schema.registry");
	public static final String AGENT_REGISTRATION_TOPIC = Main.getProperty("km.agent-registration.kafka.topic");
	public static final String DEVICE_REGISTRATION_TOPIC = Main.getProperty("km.device-registration.kafka.topic");

	public static <V> Producer<String, V> createSchemaRegistryProducer(String clientId) {
		if (Strings.isNullOrEmpty(BOOTSTRAP_SERVERS)) {
			LOG.warn("No Kafka boostrap servers configured, returning mock producer");
			return new MockProducer<>();
		}
		Properties props = new Properties();
		props.put(ProducerConfig.CLIENT_ID_CONFIG, clientId);
		props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
		props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, KafkaAvroSerializer.class);

		props.putAll(getAvroConfig());

		return new KafkaProducer<>(props);
	}

	private static Map<String, Object> getAvroConfig() {
		Map<String, Object> map = new HashMap<>();
		map.put(AbstractKafkaAvroSerDeConfig.SCHEMA_REGISTRY_URL_CONFIG, SCHEMA_REGISTRY);
		map.put(AbstractKafkaAvroSerDeConfig.AUTO_REGISTER_SCHEMAS, false);
		map.put(AbstractKafkaAvroSerDeConfig.VALUE_SUBJECT_NAME_STRATEGY, CustomNameStrategy.class);
		return map;
	}

	public static KafkaAvroSerializer getAvroValueSerializer() {
		KafkaAvroSerializer ser = new KafkaAvroSerializer();
		ser.configure(getAvroConfig(), false);
		return ser;
	}

	public static class CustomNameStrategy extends RecordNameStrategy {
		@Override
		public String subjectName(String topic, boolean isKey, Schema schema) {
			return super.subjectName(topic, isKey, schema).replace(".", "-"); // see schema registration in schema config container
		}
	}

}
