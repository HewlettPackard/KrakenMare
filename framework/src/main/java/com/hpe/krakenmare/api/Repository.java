package com.hpe.krakenmare.api;

import java.util.List;
import java.util.UUID;

public interface Repository<T> {

	void reset();

	T create(T payload);

	boolean save(T entity);

	T update(T entity);

	boolean delete(T entity);

	T get(UUID uuid);

	List<T> getAll();

	default long count() {
		return getAll().size();
	}

}
