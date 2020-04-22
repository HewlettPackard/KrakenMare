package com.hpe.krakenmare.impl;

import java.security.GeneralSecurityException;
import java.util.List;

import org.apache.kafka.clients.producer.Producer;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.api.Framework;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.repositories.AgentRedisRepository;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

public class FrameworkImpl implements Framework {

	public final static Logger LOG = LoggerFactory.getLogger(FrameworkImpl.class);

	private static final HostAndPort hp = HostAndPort.parseString(Main.getProperty("redis.server"));
	private final JedisPool pool = new JedisPool(new JedisPoolConfig(), hp.getHost(), hp.getPort());
	private final AgentRedisRepository agents = new AgentRedisRepository(pool);
	private final FrameworkMqttClient mqttListener = new FrameworkMqttClient();

	private final Producer<String, byte[]> kafkaProducer = KafkaUtils.createByteArrayProducer("framework-manager");

	public void startFramework() throws InterruptedException, MqttException, GeneralSecurityException {
		mqttListener.start();

		MqttRegistrationListener.registerNew(mqttListener, kafkaProducer, agents);
		MqttDeviceListListener.registerNew(mqttListener, kafkaProducer, agents);
		MqttDeregistrationListener.registerNew(mqttListener, kafkaProducer, agents);
	}

	public void stopFramework() {
		mqttListener.stop();
		kafkaProducer.close();
		pool.close();
	}

	@Override
	public List<Agent> getAgents() {
		return agents.getAll();
	}

}
