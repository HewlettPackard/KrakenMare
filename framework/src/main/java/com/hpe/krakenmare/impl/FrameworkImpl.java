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
import com.hpe.krakenmare.message.manager.DeviceListResponse;
import com.hpe.krakenmare.message.manager.RegisterResponse;
import com.hpe.krakenmare.repositories.AgentRedisRepository;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.Jedis;

public class FrameworkImpl implements Framework {

	public final static Logger LOG = LoggerFactory.getLogger(FrameworkImpl.class);

	private final Jedis jedis = new Jedis(HostAndPort.parseString(Main.getProperty("redis.server")));
	private final AgentRedisRepository agents = new AgentRedisRepository(jedis);
	private final FrameworkMqttClient mqttListener = new FrameworkMqttClient();

	private final Producer<String, RegisterResponse> agentKafkaProducer = KafkaUtils.createSchemaRegistryProducer("framework-agent-registration");
	private final Producer<String, DeviceListResponse> deviceKafkaProducer = KafkaUtils.createSchemaRegistryProducer("framework-device-registration");

	private final CollectdTransformStream collectdStream = new CollectdTransformStream();

	public void startFramework() throws InterruptedException, MqttException, GeneralSecurityException {
		mqttListener.start();
		collectdStream.start();

		MqttRegistrationListener.registerNew(mqttListener, agentKafkaProducer, agents);
		MqttDeviceListListener.registerNew(mqttListener, deviceKafkaProducer, agents);
	}

	public void stopFramework() {
		collectdStream.close();
		mqttListener.stop();
		agentKafkaProducer.close();
		deviceKafkaProducer.close();
	}

	@Override
	public List<Agent> getAgents() {
		return agents.getAll();
	}

}
