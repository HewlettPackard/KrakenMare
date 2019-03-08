package com.hpe.pathforward.agent;

import java.util.Date;

import com.hpe.cmu.core.Resource;
import com.hpe.cmu.core.exception.InvalidAttributeException;

public class Agent extends Resource {

	private static final long serialVersionUID = -8360318815713463421L;

	public Agent(String name, long id) throws InvalidAttributeException {
		super(name, null);
		this.setId(id);
		setCreationTime(new Date());
	}

}
