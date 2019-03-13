package com.hpe.bluedragon.repositories;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.bluedragon.api.Repository;
import com.hpe.bluedragon.core.Agent;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.Pipeline;
import redis.clients.jedis.Response;
import redis.clients.jedis.Transaction;

public class AgentRedisRepository implements Repository<Agent> {

	public final static Logger LOG = LoggerFactory.getLogger(AgentRedisRepository.class);

	private final Jedis jedis;
	private final String counterKey = "myCounterKey";
	private final String agentsKey = "myAgentsKey";
	private final String agentDataKey = "myAgentDataKey";

	public AgentRedisRepository(Jedis jedis) {
		this.jedis = jedis;
	}

	@Override
	public Agent create(String name) {
		long id = jedis.incr(counterKey);
		LOG.info("Creating new agent: name='{}', id='{}'", name, id);
		return new Agent(id, name + "-" + id);
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

	// TODO: make this in a transaction?
	@Override
	public List<Agent> getAll() {
		List<Agent> agents = new ArrayList<>();
		List<String> allUserIds = jedis.lrange(agentsKey, 0, -1);
		if (allUserIds != null && !allUserIds.isEmpty()) {
			List<Response<Map<String, String>>> responseList = new ArrayList<>();

			Pipeline pipeline = jedis.pipelined();
			for (String id : allUserIds) {
				String agentKey = agentDataKey + ":" + id;
				responseList.add(pipeline.hgetAll(agentKey));
			}
			pipeline.sync();

			for (Response<Map<String, String>> response : responseList) {
				agents.add(Agent.fromMap(response.get()));
			}
		}
		return agents;
	}

}
