package com.hpe.bluedragon.api;

import java.util.List;

public interface Repository<T> {

	T create(String id);

	boolean save(T entity);

	T update(T entity);

	boolean delete(T entity);

	T get(long id);

	List<T> getAll();

	default long count() {
		return getAll().size();
	}

}
