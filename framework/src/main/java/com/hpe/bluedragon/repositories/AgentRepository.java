package com.hpe.bluedragon.repositories;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.bluedragon.api.Repository;
import com.hpe.bluedragon.core.Agent;

public class AgentRepository implements Repository<Agent> {

	public final static Logger LOG = LoggerFactory.getLogger(AgentRepository.class);

	private final AtomicLong index = new AtomicLong();
	private final List<Agent> agents = new ArrayList<>();

	@Override
	public Agent create(String name) {
		long id = index.getAndIncrement();
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
