package com.hpe.bluedragon.repositories;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.bluedragon.api.Repository;
import com.hpe.bluedragon.core.Agent;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.Response;
import redis.clients.jedis.Transaction;

public class AgentRedisRepository implements Repository<Agent> {

	public final static Logger LOG = LoggerFactory.getLogger(AgentRedisRepository.class);

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
	public Agent create(String name, UUID uuid) {
		long id = jedis.incr(counterKey);
		LOG.info("Creating new agent: id='{}', name='{}', uuid='{}'", id, name, uuid);
		return new Agent(id, uuid, name);
	}

	@Override
	public boolean save(Agent agent) {
		String agentKey = agentDataKey + ":" + agent.getId();

		try (Transaction t = jedis.multi()) {
			t.rpush(agentsKey, String.valueOf(agent.getId()));
			t.hmset(agentKey, agent.toMap());
			t.exec();
		}

		return true;
	}

	@Override
	public Agent update(Agent agent) {
		String agentKey = agentDataKey + ":" + agent.getId();
		jedis.hmset(agentKey, agent.toMap());
		return agent;
	}

	@Override
	public boolean delete(Agent agent) {
		String agentKey = agentDataKey + ":" + agent.getId();

		try (Transaction t = jedis.multi()) {
			Response<Long> responseDel = t.del(agentKey);
			Response<Long> responseLrem = t.lrem(agentsKey, 0, String.valueOf(agent.getId()));
			t.exec();

			return responseDel.get() == 1 && responseLrem.get() == 1;
		}
	}

	@Override
	public Agent get(long id) {
		String agentKey = agentDataKey + ":" + id;
		Map<String, String> map = jedis.hgetAll(agentKey);
		return Agent.fromMap(map);
	}

	@Override
	public long count() {
		return jedis.llen(agentsKey);
	}

	@Override
	public List<Agent> getAll() {
		String script = "local collect = {}\n" +
				"local keys = redis.call('lrange', '" + agentsKey + "', 0, -1)\n" +
				"for _, key in ipairs(keys) do \n" +
				"    local value = redis.call('hgetAll', '" + agentDataKey + ":' .. key)\n" +
				"    if value then\n" +
				"        table.insert(collect, value)\n" +
				"    end \n" +
				"end \n" +
				"return collect";

		@SuppressWarnings("unchecked")
		List<List<String>> result = (List<List<String>>) jedis.eval(script);
		List<Agent> agents = result.stream().map(Agent::fromList).collect(Collectors.toList());
		return agents;
	}

	@Override
	public void reset() {
		jedis.del(counterKey, agentsKey, agentDataKey);
	}

}
