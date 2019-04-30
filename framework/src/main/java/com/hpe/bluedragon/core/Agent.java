package com.hpe.bluedragon.core;

import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.collect.ImmutableMap;

public class Agent {

	private final long id;
	private final UUID uuid;
	private final String name;

	@JsonCreator
	public Agent(@JsonProperty("id") long id,
			@JsonProperty("uuid") UUID uuid,
			@JsonProperty("name") String name) {
		this.id = id;
		this.uuid = uuid;
		this.name = name;
	}

	public long getId() {
		return id;
	}

	public UUID getUuid() {
		return uuid;
	}

	public String getName() {
		return name;
	}

	public Map<String, String> toMap() {
		return ImmutableMap.of("id", String.valueOf(id),
				"uuid", uuid.toString(),
				"name", name);
	}

	public static Agent fromMap(Map<String, String> map) {
		long id = Long.parseLong(map.get("id"));
		UUID uuid = UUID.fromString(map.get("uuid"));
		String name = map.get("name");
		return new Agent(id, uuid, name);
	}

	public static Agent fromList(List<String> list) {
		final Map<String, String> hash = new HashMap<>(list.size() / 2, 1);
		final Iterator<String> iterator = list.iterator();
		while (iterator.hasNext()) {
			hash.put(iterator.next(), iterator.next());
		}
		return fromMap(hash);
	}

}
