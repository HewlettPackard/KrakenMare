package com.hpe.bluedragon.impl;

import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.bluedragon.Main;
import com.hpe.bluedragon.api.Framework;
import com.hpe.bluedragon.core.Agent;
import com.hpe.bluedragon.repositories.AgentRedisRepository;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.Jedis;

public class FrameworkImpl implements Framework {

	public final static Logger LOG = LoggerFactory.getLogger(FrameworkImpl.class);

	private final Jedis jedis = new Jedis(HostAndPort.parseString(Main.PROPERTIES.getProperty("redis.server")));
	private final AgentRedisRepository agents = new AgentRedisRepository(jedis);
	private final KafkaRegistrationStream registrationStream = new KafkaRegistrationStream(agents);

	public void startFramework() throws InterruptedException {
		registrationStream.start();
	}

	public void stopFramework() {
		registrationStream.close();
	}

	@Override
	public List<Agent> getAgents() {
		return agents.getAll();
	}

}
