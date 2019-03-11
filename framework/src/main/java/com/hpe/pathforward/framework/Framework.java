package com.hpe.pathforward.framework;

import static com.hpe.pathforward.Main.PROPERTIES;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
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

import com.hpe.pathforward.agent.Agent;
import com.hpe.pathforward.agent.AgentFactory;
import com.hpe.pathforward.serde.JsonPOJODeserializer;
import com.hpe.pathforward.serde.JsonPOJOSerializer;

public class Framework {

	public final static Logger LOG = LoggerFactory.getLogger(Framework.class);

	private final AgentFactory factory = new AgentFactory();
	private final Set<Agent> agents = new LinkedHashSet<>();

	private KafkaStreams streams;

	public void startFramework() throws InterruptedException {
		final String requestTopicName = PROPERTIES.getProperty("pf.registration.request-topic");
		final String resultTopicName = PROPERTIES.getProperty("pf.registration.result-topic");

		LOG.info("Creating topics...");
		try (AdminClient adminClient = AdminClient.create(PROPERTIES)) {
			NewTopic requestTopic = new NewTopic(requestTopicName, 1, (short) 1);
			NewTopic resultTopic = new NewTopic(resultTopicName, 1, (short) 1);

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

		final Serde<String> stringSerde = Serdes.String();

		final Serializer<Agent> agentSerializer = new JsonPOJOSerializer<>();
		final Deserializer<Agent> agentDeserializer = new JsonPOJODeserializer<>();
		final Serde<Agent> agentSerde = Serdes.serdeFrom(agentSerializer, agentDeserializer);

		final StreamsBuilder builder = new StreamsBuilder();
		final KStream<String, String> source = builder.stream(requestTopicName, Consumed.with(stringSerde, stringSerde));

		source.mapValues(this::registerNewAgent)
				.to(resultTopicName, Produced.with(stringSerde, agentSerde));

		final Topology topology = builder.build();
		LOG.info(topology.describe().toString());

		LOG.info("Starting streams...");
		streams = new KafkaStreams(topology, PROPERTIES);

		streams.setUncaughtExceptionHandler((Thread thread, Throwable throwable) -> {
			// TODO
			// here you should examine the throwable/exception and perform an appropriate action!
		});

		// finally kick start the app
		streams.start();
	}

	public void stopFramework() {
		if (streams != null) {
			LOG.info("Stopping streams...");
			streams.close();
		}
	}

	private Agent registerNewAgent(String name) {
		Agent agent = factory.create(name);
		agents.add(agent);
		return agent;
	}

	public Set<Agent> getAgents() {
		return agents;
	}

}
