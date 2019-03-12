package com.hpe.bluedragon.rest;

import java.util.List;

import javax.inject.Inject;
import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.bluedragon.api.Framework;
import com.hpe.bluedragon.core.Agent;

@Path("agents")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class AgentsResource {

	public final static Logger LOG = LoggerFactory.getLogger(AgentsResource.class);

	@Inject
	private Framework framework;

	@GET
	public List<Agent> getAll() {
		LOG.info("Entering getAll()");
		return framework.getAgents();
	}

}
