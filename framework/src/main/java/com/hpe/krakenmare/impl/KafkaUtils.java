package com.hpe.krakenmare.impl;

import java.util.Properties;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.MockProducer;
import org.apache.kafka.clients.producer.Producer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.LongSerializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.base.Strings;
import com.hpe.krakenmare.Main;

public class KafkaUtils {

	public final static Logger LOG = LoggerFactory.getLogger(KafkaUtils.class);

	public static final String BOOTSTRAP_SERVERS = Main.getProperty("bootstrap.servers");
	public static final String REGISTRATION_TOPIC = Main.getProperty("km.registration.kafka.topic");
	public static final String SENSOR_LIST_TOPIC = Main.getProperty("km.device-registration.kafka.topic");

	public static <K, V> Producer<K, V> createProducer(String clientId) {
		if (Strings.isNullOrEmpty(BOOTSTRAP_SERVERS)) {
			LOG.warn("No Kafka boostrap servers configured, returning mock producer");
			return new MockProducer<>();
		}
		Properties props = new Properties();
		props.put(ProducerConfig.CLIENT_ID_CONFIG, clientId);
		props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
		props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, LongSerializer.class.getName());
		props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		return new KafkaProducer<>(props);
	}

}
