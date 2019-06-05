package com.hpe.bluedragon.impl;

import java.time.Duration;
import java.util.Properties;

import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.Materialized;
import org.apache.kafka.streams.kstream.Produced;
import org.apache.kafka.streams.kstream.TimeWindows;
import org.apache.kafka.streams.kstream.Windowed;
import org.apache.kafka.streams.kstream.WindowedSerdes;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.hpe.bluedragon.Main;
import com.hpe.bluedragon.serde.JsonSerdes;

public class CollectdTransformStream {

	private final static Logger LOG = LoggerFactory.getLogger(CollectdTransformStream.class);
	private final static Properties PROPERTIES = Main.cloneProperties();
	static {
		PROPERTIES.put("application.id", "bd-collectd-druid");
		PROPERTIES.put("default.deserialization.exception.handler", "org.apache.kafka.streams.errors.LogAndContinueExceptionHandler");
		PROPERTIES.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 10 * 1000);
		PROPERTIES.put(StreamsConfig.TOPOLOGY_OPTIMIZATION, StreamsConfig.OPTIMIZE);
	}

	public final static String READ_TOPIC = "collectd";
	public final static String WRITE_TOPIC = "collectd-druid";

	private final static Duration windowSize = Duration.ofSeconds(10);
	private final static Duration windowGrace = Duration.ofSeconds(2);

	private final static ObjectMapper MAPPER = new ObjectMapper();

	private KafkaStreams streams;

	public CollectdTransformStream() {
		final Serde<String> stringSerde = Serdes.String();
		final Serde<JsonNode> jsonNodeSerde = JsonSerdes.JsonNode();
		final Serde<ObjectNode> objectNodeSerde = JsonSerdes.ObjectNode();
		final Serde<Windowed<String>> windowSerde = WindowedSerdes.sessionWindowedSerdeFrom(String.class);

		// TODO time extractor?

		final StreamsBuilder builder = new StreamsBuilder();
		builder.stream(READ_TOPIC, Consumed.with(stringSerde, jsonNodeSerde))
				.groupByKey()
				.windowedBy(TimeWindows.of(windowSize).grace(windowGrace))
				.aggregate(this::druidInitializer,
						this::druidAggregator,
						Materialized.with(stringSerde, objectNodeSerde))
				.toStream()
				.to(WRITE_TOPIC, Produced.with(windowSerde, objectNodeSerde));

		final Topology topology = builder.build();
		LOG.info(topology.describe().toString());

		streams = new KafkaStreams(topology, PROPERTIES);

		streams.setUncaughtExceptionHandler((Thread thread, Throwable throwable) -> {
			LOG.error("In thread " + thread.getName(), throwable);
		});
	}

	public void start() throws InterruptedException {
		LOG.info("Starting streams...");
		streams.start();
	}

	public void close() {
		LOG.info("Stopping streams...");
		streams.close();
	}

	// Initializer<VR> initializer
	private ObjectNode druidInitializer() {
		LOG.trace("Creating new aggregation node");
		return MAPPER.createObjectNode();
	}

	// Aggregator<? super K, ? super V, VR> aggregator
	private ObjectNode druidAggregator(String key, JsonNode value, ObjectNode aggregate) {
		LOG.trace("Aggregating for key '" + key + "':\n\tvalue = " + value + "\n\taggregate = " + aggregate);

		JsonNode input = value.get(0);
		String host = input.get("host").textValue();
		float v = input.get("values").get(0).floatValue();
		long time = (long) (input.get("time").doubleValue() * 1000d);
		long interval = input.get("interval").longValue();
		String plugin = input.get("plugin").textValue();
		String type_instance = input.get("type_instance").textValue();
		String type = input.get("type").textValue();

		aggregate.put("time", time);
		aggregate.put("host", host);
		aggregate.put(plugin + ":" + type_instance, v);
		aggregate.put("interval", interval);
		aggregate.put("type", type);

		return aggregate;
	}

}
