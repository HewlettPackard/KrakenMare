package com.hpe.krakenmare.api;

import java.util.UUID;

public class EntityNotFoundException extends FrameworkException {

	private static final long serialVersionUID = 2092919960846853909L;

	private final UUID uuid;

	public EntityNotFoundException(UUID uuid) {
		super("Entity not found for UUID: " + uuid);
		this.uuid = uuid;
	}

	public UUID getUuid() {
		return uuid;
	}

}
