package com.hpe.krakenmare.api;

import java.util.List;
import java.util.UUID;

public interface Repository<T> {

	void reset();

	default T create(String id) {
		UUID uuid = UUID.randomUUID();
		return create(id, uuid);
	}

	T create(CharSequence id, UUID uuid);

	boolean save(T entity);

	T update(T entity);

	boolean delete(T entity);

	T get(long id);

	List<T> getAll();

	default long count() {
		return getAll().size();
	}

}
