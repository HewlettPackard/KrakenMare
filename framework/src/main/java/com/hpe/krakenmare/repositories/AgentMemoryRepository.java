package com.hpe.krakenmare.repositories;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.EntityNotFoundException;
import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;

public class AgentMemoryRepository implements Repository<Agent> {

	public final static Logger LOG = LoggerFactory.getLogger(AgentMemoryRepository.class);

	private final AtomicLong index = new AtomicLong();
	private final List<Agent> agents = new ArrayList<>();

	@Override
	public synchronized void reset() {
		index.set(0);
		agents.clear();
	}

	@Override
	public synchronized Agent create(Agent payload) {
		long id = index.getAndIncrement();
		UUID uuid = UUID.randomUUID();
		LOG.info("Creating new agent: id='{}', uid='{}', uuid='{}', name='{}'", id, payload.getUid(), uuid, payload.getName());
		return new Agent(id, payload.getUid(), uuid, payload.getName(), Collections.emptyList());
	}

	@Override
	public synchronized boolean save(Agent agent) {
		return agents.add(agent);
	}

	@Override
	public synchronized boolean delete(Agent agent) {
		LOG.info("Deleting agent: id='{}', uid='{}', uuid='{}', name='{}'", agent.getId(), agent.getUid(), agent.getUuid(), agent.getName());
		return agents.remove(agent);
	}

	@Override
	public synchronized List<Agent> getAll() {
		return agents;
	}

	@Override
	public synchronized Agent update(Agent agent) {
		// no-op
		return agent;
	}

	@Override
	public synchronized Agent get(UUID uuid) throws EntityNotFoundException {
		Optional<Agent> opt = agents.stream().filter(a -> a.getUuid().equals(uuid)).findFirst();
		if (!opt.isPresent()) {
			throw new EntityNotFoundException(uuid);
		}
		return opt.get();
	}

}
