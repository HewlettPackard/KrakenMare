package com.hpe.bluedragon.impl;

import static com.hpe.bluedragon.Main.PROPERTIES;

import java.util.ArrayList;
import java.util.List;
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

import com.hpe.bluedragon.Main;
import com.hpe.bluedragon.api.Framework;
import com.hpe.bluedragon.core.Agent;
import com.hpe.bluedragon.repositories.AgentRedisRepository;
import com.hpe.bluedragon.serde.JsonPOJODeserializer;
import com.hpe.bluedragon.serde.JsonPOJOSerializer;

import redis.clients.jedis.HostAndPort;
import redis.clients.jedis.Jedis;

public class FrameworkImpl implements Framework {

	public final static Logger LOG = LoggerFactory.getLogger(FrameworkImpl.class);

	private final Jedis jedis = new Jedis(HostAndPort.parseString(Main.PROPERTIES.getProperty("redis.server")));
	private final AgentRedisRepository agents = new AgentRedisRepository(jedis);

	private KafkaStreams streams;


	public void startFramework() throws InterruptedException {
		final String requestTopicName = PROPERTIES.getProperty("bd.registration.request-topic");
		final String resultTopicName = PROPERTIES.getProperty("bd.registration.result-topic");

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
		Agent agent = agents.create(name);
		agents.save(agent);
		return agent;
	}

	@Override
	public List<Agent> getAgents() {
		return agents.getAll();
	}

}
