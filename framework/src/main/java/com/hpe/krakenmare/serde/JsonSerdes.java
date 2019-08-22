package com.hpe.krakenmare.serde;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serdes.WrapperSerde;
import org.apache.kafka.common.serialization.Serializer;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;

public class JsonSerdes {

	static public final class JsonNodeSerde extends WrapperSerde<JsonNode> {
		public JsonNodeSerde() {
			super(new JsonNodeSerializer(), new JsonNodeDeserializer());
		}
	}

	static public final class ObjectNodeSerde extends WrapperSerde<ObjectNode> {
		public ObjectNodeSerde() {
			super(new ObjectNodeSerializer(), new ObjectNodeDeserializer());
		}
	}

	static public Serde<JsonNode> JsonNode() {
		return new JsonNodeSerde();
	}

	static public Serde<ObjectNode> ObjectNode() {
		return new ObjectNodeSerde();
	}

	static public <T> Serde<T> Pojo(Class<T> clazz) {
		final Serializer<T> ser = new JsonPOJOSerializer<>();
		final Deserializer<T> de = new JsonPOJODeserializer<>();
		// TODO: do better, we should not need to explicitly configure deserializer type here...
		Map<String, Object> serdeProps = new HashMap<>();
		serdeProps.put("JsonPOJOClass", clazz);
		de.configure(serdeProps, false);

		return Serdes.serdeFrom(ser, de);
	}

}
