package com.hpe.bluedragon.agent;

public class Agent {

	private final long id;
	private final String name;

	public Agent(String name, long id) {
		this.name = name;
		this.id = id;
	}

	public long getId() {
		return id;
	}

	public String getName() {
		return name;
	}

}
