package com.hpe.krakenmare.rest;

import java.io.IOException;

import javax.ws.rs.ext.ContextResolver;
import javax.ws.rs.ext.Provider;

import org.apache.avro.util.Utf8;

import com.fasterxml.jackson.annotation.JsonAutoDetect.Visibility;
import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.PropertyAccessor;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.databind.SerializerProvider;
import com.fasterxml.jackson.databind.annotation.JsonSerialize;

@Provider
public class ObjectMapperContextResolver implements ContextResolver<ObjectMapper> {

	// mixin to define Utf8(String string) as a JSON creator
	@JsonSerialize(using = Utf8Serializer.class)
	private static class Utf8Mixin {
		@JsonCreator
		public Utf8Mixin(String string) {
		}
	}

	private static class Utf8Serializer extends JsonSerializer<Utf8> {
		@Override
		public void serialize(Utf8 value, JsonGenerator jgen, SerializerProvider provider) throws IOException, JsonProcessingException {
			provider.defaultSerializeValue(value.toString(), jgen);
		}

		@Override
		public boolean isEmpty(SerializerProvider provider, Utf8 value) {
			return value == null;
		}

		@Override
		public Class<Utf8> handledType() {
			return Utf8.class;
		}
	}

	private static final ObjectMapper MAPPER = new ObjectMapper();
	static {
		MAPPER.configure(SerializationFeature.INDENT_OUTPUT, true);
		MAPPER.setVisibility(PropertyAccessor.ALL, Visibility.NONE);
		MAPPER.setVisibility(PropertyAccessor.FIELD, Visibility.ANY);
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
