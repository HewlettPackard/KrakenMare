package com.hpe.krakenmare.impl;

import java.util.List;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.api.Framework;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.repositories.AgentRedisRepository;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.Jedis;

public class FrameworkImpl implements Framework {

	public final static Logger LOG = LoggerFactory.getLogger(FrameworkImpl.class);

	private final Jedis jedis = new Jedis(HostAndPort.parseString(Main.getProperty("redis.server")));
	private final AgentRedisRepository agents = new AgentRedisRepository(jedis);
	private final FrameworkMqttClient mqttListener = new FrameworkMqttClient();

	private final KafkaProducer<String, byte[]> kafkaProducer = KafkaUtils.createProducer("framework-manager");

	private final CollectdTransformStream collectdStream = new CollectdTransformStream();

	public void startFramework() throws InterruptedException, MqttException {
		mqttListener.start();
		collectdStream.start();

		MqttRegistrationListener.registerNew(mqttListener, kafkaProducer, agents);
		MqttDeviceListListener.registerNew(mqttListener, kafkaProducer, agents);
	}

	public void stopFramework() {
		collectdStream.close();
		mqttListener.stop();
		kafkaProducer.close();
	}

	@Override
	public List<Agent> getAgents() {
		return agents.getAll();
	}

}
