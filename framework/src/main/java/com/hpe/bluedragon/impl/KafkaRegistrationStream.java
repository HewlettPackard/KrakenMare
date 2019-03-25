package com.hpe.bluedragon.impl;

import static com.hpe.bluedragon.Main.PROPERTIES;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;

import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.CreateTopicsResult;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.kafka.common.KafkaFuture;
import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.common.serialization.Serializer;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Produced;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.bluedragon.core.Agent;
import com.hpe.bluedragon.repositories.AgentRedisRepository;
import com.hpe.bluedragon.serde.JsonPOJODeserializer;
import com.hpe.bluedragon.serde.JsonPOJOSerializer;

public class KafkaRegistrationStream {

	public final static Logger LOG = LoggerFactory.getLogger(KafkaRegistrationStream.class);

	public final static String REQUEST_TOPIC = PROPERTIES.getProperty("bd.registration.request-topic");
	public final static String RESULT_TOPIC = PROPERTIES.getProperty("bd.registration.result-topic");

	private final AgentRedisRepository repository;
	private KafkaStreams streams;

	public KafkaRegistrationStream(AgentRedisRepository repository) {
		this.repository = repository;

		final Serde<String> stringSerde = Serdes.String();

		final Serializer<Agent> agentSerializer = new JsonPOJOSerializer<>();
		// TODO: do better, we should not need to explicitly configure deserializer type here...
		final Deserializer<Agent> agentDeserializer = new JsonPOJODeserializer<>();
		Map<String, Object> serdeProps = new HashMap<>();
		serdeProps.put("JsonPOJOClass", Agent.class);
		agentDeserializer.configure(serdeProps, false);

		final Serde<Agent> agentSerde = Serdes.serdeFrom(agentSerializer, agentDeserializer);

		final StreamsBuilder builder = new StreamsBuilder();
		final KStream<String, Agent> source = builder.stream(REQUEST_TOPIC, Consumed.with(stringSerde, agentSerde));

		source.mapValues(this::registerNewAgent)
				.to(RESULT_TOPIC, Produced.with(stringSerde, agentSerde));

		final Topology topology = builder.build();
		LOG.info(topology.describe().toString());

		PROPERTIES.put("default.deserialization.exception.handler", "org.apache.kafka.streams.errors.LogAndContinueExceptionHandler");
		streams = new KafkaStreams(topology, PROPERTIES);

		streams.setUncaughtExceptionHandler((Thread thread, Throwable throwable) -> {
			// TODO
			// here you should examine the throwable/exception and perform an appropriate action!
		});
	}

	private Agent registerNewAgent(Agent payload) {
		Agent agent = repository.create(payload.getName());
		repository.save(agent);
		return agent;
	}

	public void start() throws InterruptedException {
		LOG.info("Creating topics...");
		try (AdminClient adminClient = AdminClient.create(PROPERTIES)) {
			NewTopic requestTopic = new NewTopic(REQUEST_TOPIC, 1, (short) 1);
			NewTopic resultTopic = new NewTopic(RESULT_TOPIC, 1, (short) 1);

			List<NewTopic> newTopics = new ArrayList<>();
			newTopics.add(requestTopic);
			newTopics.add(resultTopic);

			CreateTopicsResult result = adminClient.createTopics(newTopics);
			// wait for creation completion
			for (KafkaFuture<Void> f : result.values().values()) {
				try {
					f.get();
				} catch (ExecutionException e) {
					LOG.warn("Unable to create topic", e);
				}
			}
		}
		LOG.info("Starting streams...");
		streams.start();
	}

	public void close() {
		LOG.info("Stopping streams...");
		streams.close();
	}

}
