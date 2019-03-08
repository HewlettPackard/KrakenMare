package com.hpe.pathforward.framework;

import java.util.concurrent.atomic.AtomicLong;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.cmu.core.exception.InvalidAttributeException;
import com.hpe.pathforward.agent.Agent;

public class AgentFactory {

	public final static Logger LOG = LoggerFactory.getLogger(AgentFactory.class);

	private final AtomicLong index = new AtomicLong();

	public Agent create(String name) {
		long id = index.getAndIncrement();
		LOG.info("Creating new agent with id: " + id);
		try {
			return new Agent(name + "-" + id, id);
		} catch (InvalidAttributeException e) {
			// won't happen since we build a valid name
			LOG.error("Unable to create agent", e);
			return null;
		}
	}

}
