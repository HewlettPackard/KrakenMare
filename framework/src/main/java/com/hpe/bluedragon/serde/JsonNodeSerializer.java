/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements. See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.hpe.bluedragon.serde;

import java.util.Map;

import org.apache.kafka.common.errors.SerializationException;
import org.apache.kafka.common.serialization.Serializer;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class JsonNodeSerializer implements Serializer<JsonNode> {

	private final ObjectMapper objectMapper = new ObjectMapper();

	/**
	 * Default constructor needed by Kafka
	 */
	public JsonNodeSerializer() {
	}

	@Override
	public void configure(Map<String, ?> props, boolean isKey) {
	}

	@Override
	public byte[] serialize(String topic, JsonNode node) {
		if (node == null) {
			return null;
		}

		try {
			return objectMapper.writeValueAsBytes(node);
		} catch (Exception e) {
			throw new SerializationException("Error serializing JSON message", e);
		}
	}

	@Override
	public void close() {
	}

}
