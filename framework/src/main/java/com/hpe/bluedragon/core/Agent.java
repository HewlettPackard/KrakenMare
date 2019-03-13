package com.hpe.bluedragon.core;

import java.util.Map;

import com.google.common.collect.ImmutableMap;

public class Agent {

	private final long id;
	private final String name;

	public Agent(long id, String name) {
		this.id = id;
		this.name = name;
	}

	public long getId() {
		return id;
	}

	public String getName() {
		return name;
	}

	public Map<String, String> toMap() {
		return ImmutableMap.of("id", String.valueOf(id), "name", name);
	}

	public static Agent fromMap(Map<String, String> map) {
		long id = Long.parseLong(map.get("id"));
		String name = map.get("name");
		return new Agent(id, name);
	}

}
