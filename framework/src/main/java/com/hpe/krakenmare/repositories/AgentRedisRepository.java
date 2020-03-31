package com.hpe.krakenmare.repositories;

import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.hpe.krakenmare.api.EntityNotFoundException;
import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;
import com.hpe.krakenmare.rest.ObjectMapperContextResolver;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

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

	private final JedisPool jpool;
	private final String counterKey = "myCounterKey";
	private final String agentsKey = "myAgentsKey";
	private final String agentDataKey = "myAgentDataKey";

	public AgentRedisRepository(JedisPool jedis) {
		this(jedis, false);
	}

	public AgentRedisRepository(JedisPool jedis, boolean reset) {
		this.jpool = jedis;
		if (reset) {
			reset();
		}
	}

	@Override
	public Agent create(Agent payload) {
		long id = -1;
		try (Jedis jedis = jpool.getResource()) {
			id = jedis.incr(counterKey);
		}
		UUID uuid = UUID.randomUUID();
		LOG.info("Creating new agent: id='{}', uid='{}', uuid='{}', name='{}'", id, payload.getUid(), uuid, payload.getName());
		return new Agent(id, payload.getUid(), uuid, payload.getName(), Collections.emptyList());
	}

	@Override
	public boolean save(Agent agent) {
		String agentKey = agentDataKey + ":" + agent.getUuid();
		String json = toJson(agent);
		try (Jedis jedis = jpool.getResource()) {
			return jedis.hset(agentsKey, agentKey, json) == 1;
		}
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
		try (Jedis jedis = jpool.getResource()) {
			return jedis.hdel(agentsKey, agentKey) == 1;
		}
	}

	@Override
	public Agent get(UUID uuid) throws EntityNotFoundException {
		String agentKey = agentDataKey + ":" + uuid;

		String json = null;
		try (Jedis jedis = jpool.getResource()) {
			json = jedis.hget(agentsKey, agentKey);
		}
		if (json == null) {
			throw new EntityNotFoundException(uuid);
		}
		return fromJson(json);
	}

	@Override
	public long count() {
		try (Jedis jedis = jpool.getResource()) {
			return jedis.hlen(agentsKey);
		}
	}

	@Override
	public List<Agent> getAll() {
		Map<String, String> result = null;
		try (Jedis jedis = jpool.getResource()) {
			result = jedis.hgetAll(agentsKey);
		}
		return result.values()
				.stream()
				.map(AgentRedisRepository::fromJson)
				.collect(Collectors.toList());
	}

	@Override
	public void reset() {
		try (Jedis jedis = jpool.getResource()) {
			jedis.del(counterKey, agentsKey, agentDataKey);
		}
	}

}
