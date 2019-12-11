package com.hpe.krakenmare.impl;

import java.util.Properties;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.LongSerializer;
import org.apache.kafka.common.serialization.StringSerializer;

import com.hpe.krakenmare.Main;

public class KafkaUtils {

	public static final String BOOTSTRAP_SERVERS = Main.getProperty("bootstrap.servers");
	public static final String REGISTRATION_TOPIC = Main.getProperty("km.registration.kafka.topic");
	public static final String SENSOR_LIST_TOPIC = Main.getProperty("km.device-registration.kafka.topic");

	public static <K, V> KafkaProducer<K, V> createProducer(String clientId) {
		Properties props = new Properties();
		props.put(ProducerConfig.CLIENT_ID_CONFIG, clientId);
		props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, BOOTSTRAP_SERVERS);
		props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, LongSerializer.class.getName());
		props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
		return new KafkaProducer<>(props);
	}

}
