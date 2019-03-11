package com.hpe.pathforward.agent;

import java.util.concurrent.atomic.AtomicLong;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AgentFactory {

	public final static Logger LOG = LoggerFactory.getLogger(AgentFactory.class);

	private final AtomicLong index = new AtomicLong();

	public Agent create(String name) {
		long id = index.getAndIncrement();
		LOG.info("Creating new agent with id: " + id);
		return new Agent(name + "-" + id, id);
	}

}
