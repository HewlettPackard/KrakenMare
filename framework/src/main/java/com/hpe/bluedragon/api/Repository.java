package com.hpe.bluedragon.api;

import java.util.List;

public interface Repository<T> {

	T create(String id);

	boolean save(T entity);

	boolean delete(T entity);

	List<T> getAll();

	default int count() {
		return getAll().size();
	}

}
