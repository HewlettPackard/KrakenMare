package com.hpe.krakenmare.api;

import java.util.List;

public interface Repository<T> {

	void reset();

	T create(T payload);

	boolean save(T entity);

	T update(T entity);

	boolean delete(T entity);

	T get(long id);

	List<T> getAll();

	default long count() {
		return getAll().size();
	}

}
