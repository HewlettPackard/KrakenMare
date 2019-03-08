package com.hpe.cmu.server.rest.resource;

import java.util.Set;

import javax.ws.rs.GET;
import javax.ws.rs.Path;
import javax.ws.rs.core.Response;

import com.hpe.cmu.search.RuleParser;
import com.hpe.cmu.server.event.Event;
import com.hpe.cmu.server.rest.PermissionRequestFilter.PermissionRequired;
import com.hpe.cmu.server.rest.RestConstants;
import com.hpe.cmu.server.rest.search.JsonRuleParser;
import com.hpe.cmu.server.security.Permissions.Permission;
import com.hpe.pathforward.agent.Agent;
import com.hpe.pathforward.framework.Framework;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.Authorization;

@Api(tags = "Agent operations", authorizations = { @Authorization(value = RestConstants.X_AUTH_TOKEN) })
@Path("agents")
public class AgentsResource extends AbstractSearchableResource {

	private static final RuleParser<Agent, Boolean> RULE_PARSER = new JsonRuleParser<>(Agent.class);

	protected Set<Agent> search(Set<Agent> agents) {
		return search(RULE_PARSER, agents, searchQuery, false, !searchAllowsEmpty);
	}

	@ApiOperation(nickname = "getAll", value = "Lists all events", response = Event.class, responseContainer = "Set")
	@GET
	// TODO: we reuse an existing permission here as there is no support for custom permission
	// TODO: use a proper permission
	@PermissionRequired(Permission.NODE_GET)
	public Response getAll() {
		Framework framework = (Framework) service.getServiceAttribute(Framework.SERVICE_ATTRIBUTE_KEY);

		return paginated(search(framework.getAgents())).build();
	}

}
