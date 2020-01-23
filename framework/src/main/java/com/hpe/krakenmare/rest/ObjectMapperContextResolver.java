package com.hpe.krakenmare.rest;

import javax.ws.rs.ext.ContextResolver;
import javax.ws.rs.ext.Provider;

import org.apache.avro.util.Utf8;

import com.fasterxml.jackson.annotation.JsonAutoDetect.Visibility;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

@Provider
public class ObjectMapperContextResolver implements ContextResolver<ObjectMapper> {

	// mixin to define Utf8(String string) as a JSON creator
	private static class Utf8Mixin {
		@JsonCreator
		public Utf8Mixin(String string) {
		}
	}

	private static final ObjectMapper MAPPER = new ObjectMapper();
	static {
		MAPPER.configure(SerializationFeature.INDENT_OUTPUT, true);
		MAPPER.setVisibility(PropertyAccessor.ALL, Visibility.NONE);
		MAPPER.addMixIn(Utf8.class, Utf8Mixin.class);
	}

	public static ObjectMapper getCopy() {
		return MAPPER.copy();
	}

	@Override
	public ObjectMapper getContext(Class<?> type) {
		return MAPPER;
	}

}
