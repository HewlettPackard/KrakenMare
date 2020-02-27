package com.hpe.krakenmare.repositories;

import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.rest.ObjectMapperContextResolver;

import redis.clients.jedis.Jedis;

public class AgentRedisRepository implements Repository<Agent> {

	public final static Logger LOG = LoggerFactory.getLogger(AgentRedisRepository.class);

	private final static ObjectMapper MAPPER = ObjectMapperContextResolver.getCopy();

	static String toJson(Agent agent) {
		try {
			return MAPPER.writeValueAsString(agent);
		} catch (JsonProcessingException e) {
			// TODO
			throw new RuntimeException(e);
		}
	}

	static Agent fromJson(String json) {
		try {
			return MAPPER.readValue(json, Agent.class);
		} catch (IOException e) {
			// TODO
			throw new RuntimeException(e);
		}
	}

	private final Jedis jedis;
	private final String counterKey = "myCounterKey";
	private final String agentsKey = "myAgentsKey";
	private final String agentDataKey = "myAgentDataKey";

	public AgentRedisRepository(Jedis jedis) {
		this(jedis, false);
	}

	public AgentRedisRepository(Jedis jedis, boolean reset) {
		this.jedis = jedis;
		if (reset) {
			reset();
		}
	}

	@Override
	public Agent create(Agent payload) {
		long id = jedis.incr(counterKey);
		UUID uuid = UUID.randomUUID();
		LOG.info("Creating new agent: id='{}', uid='{}', uuid='{}', name='{}'", id, payload.getUid(), uuid, payload.getName());
		return new Agent(id, payload.getUid(), uuid, payload.getName(), Collections.emptyList());
	}

	@Override
	public boolean save(Agent agent) {
		String agentKey = agentDataKey + ":" + agent.getUuid();
		return jedis.hset(agentsKey, agentKey, toJson(agent)) == 1;
	}

	@Override
	public Agent update(Agent agent) {
		save(agent);
		return agent;
	}

	@Override
	public boolean delete(Agent agent) {
		LOG.info("Deleting agent: id='{}', uid='{}', uuid='{}', name='{}'", agent.getId(), agent.getUid(), agent.getUuid(), agent.getName());
		String agentKey = agentDataKey + ":" + agent.getUuid();
		return jedis.hdel(agentsKey, agentKey) == 1;
	}

	@Override
	public Agent get(UUID uuid) {
		String agentKey = agentDataKey + ":" + uuid;
		String json = jedis.hget(agentsKey, agentKey);
		return fromJson(json);
	}

	@Override
	public long count() {
		return jedis.hlen(agentsKey);
	}

	@Override
	public List<Agent> getAll() {
		return jedis.hgetAll(agentsKey)
				.values()
				.stream()
				.map(AgentRedisRepository::fromJson)
				.collect(Collectors.toList());
	}

	@Override
	public void reset() {
		jedis.del(counterKey, agentsKey, agentDataKey);
	}

}
