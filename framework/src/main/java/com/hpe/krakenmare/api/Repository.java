/**
 * (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
 */
package com.hpe.krakenmare.api;

import java.util.List;
import java.util.UUID;

public interface Repository<T> {

	void reset();

	T create(T payload);

	boolean save(T entity);

	T update(T entity);

	boolean delete(T entity);

	T get(UUID uuid) throws EntityNotFoundException;

	List<T> getAll();

	default long count() {
		return getAll().size();
	}

}
