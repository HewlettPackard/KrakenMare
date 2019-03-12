package com.hpe.bluedragon.repositories;

import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.bluedragon.Main;
import com.hpe.bluedragon.api.Repository;
import com.hpe.bluedragon.core.Agent;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.Jedis;

public class AgentRedisRepository implements Repository<Agent> {

	public final static Logger LOG = LoggerFactory.getLogger(AgentRedisRepository.class);

	private final Jedis jedis = new Jedis(HostAndPort.parseString(Main.PROPERTIES.getProperty("redis.server")));
	private final String counterKey = "myKey";
	private final List<Agent> agents = new ArrayList<>();

	public AgentRedisRepository() {
		jedis.set(counterKey, "0");
	}

	@Override
	public Agent create(String name) {
		long id = jedis.incr(counterKey);
		LOG.info("Creating new agent: name='{}', id='{}'", name, id);
		return new Agent(name + "-" + id, id);
	}

	@Override
	public boolean save(Agent agent) {
		return agents.add(agent);
	}

	@Override
	public boolean delete(Agent entity) {
		return agents.remove(entity);
	}

	@Override
	public List<Agent> getAll() {
		return agents;
	}

}
