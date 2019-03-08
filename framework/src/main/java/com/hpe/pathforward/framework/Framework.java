package com.hpe.pathforward.framework;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

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
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.Topology;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.Produced;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.base.Strings;
import com.google.common.util.concurrent.ThreadFactoryBuilder;
import com.hpe.cmu.server.api.Version;
import com.hpe.cmu.server.event.Event;
import com.hpe.cmu.server.event.ServiceStartedEvent;
import com.hpe.cmu.server.event.ServiceStoppedEvent;
import com.hpe.cmu.server.event.bus.EventListener;
import com.hpe.cmu.server.event.bus.OnServiceEvent;
import com.hpe.pathforward.agent.Agent;
import com.hpe.pathforward.serde.JsonPOJODeserializer;
import com.hpe.pathforward.serde.JsonPOJOSerializer;

public class Framework implements EventListener {

	public final static Version REQUIRED_SERVICE_VERSION = new Version(2, 1, 0);
	public final static Object SERVICE_ATTRIBUTE_KEY = new Object();

	public final static Logger LOG = LoggerFactory.getLogger(Framework.class);
	public final static Properties PROPERTIES = new Properties();
	static {
		ClassLoader classloader = Thread.currentThread().getContextClassLoader();
		try (InputStream input = classloader.getResourceAsStream("config.properties")) {
			PROPERTIES.load(input);
		} catch (IOException e) {
			LOG.error("Unable to load properties", e);
		}

		// bootstrap servers can be overridden via ENV or properties
		String bootstrapServersProp = System.getProperty("BOOTSTRAP_SERVERS");
		if (!Strings.isNullOrEmpty(bootstrapServersProp)) {
			PROPERTIES.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServersProp);
		} else {
			String bootstrapServersEnv = System.getenv("BOOTSTRAP_SERVERS");
			if (!Strings.isNullOrEmpty(bootstrapServersEnv)) {
				PROPERTIES.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServersEnv);
			}
		}
	}

	private final AgentFactory factory = new AgentFactory();
	private final Set<Agent> agents = new LinkedHashSet<>();

	private final CountDownLatch latch = new CountDownLatch(1);
	private final Executor executor = Executors.newSingleThreadExecutor(
			new ThreadFactoryBuilder().setNameFormat("framework-thread").build());

	private KafkaStreams streams;

	public Framework() {
	}

	@Override
	public Version getSupportedServiceVersion() {
		return REQUIRED_SERVICE_VERSION;
	}

	@Override
	public boolean activate() {
		// return "true".equals(System.getProperty("cmu.pf.start"));
		return true;
	}

	@OnServiceEvent(event = ServiceStartedEvent.class)
	public void startFrameworkAsync(final Event event) {
		event.getService().setServiceAttribute(SERVICE_ATTRIBUTE_KEY, this);

		executor.execute(() -> {
			try {
				startFramework();
			} catch (InterruptedException e) {
				LOG.warn("Framework interrupted", e);
			}
		});
	}

	private void startFramework() throws InterruptedException {
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
		streams.start();
		latch.await();
	}

	@OnServiceEvent(event = ServiceStoppedEvent.class)
	public void stopFramework(final Event event) {
		if (streams != null) {
			LOG.info("Stopping streams...");
			streams.close();
			latch.countDown();
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

	public static void main(String[] args) {
		new Framework().startFrameworkAsync(new Event(null) {
			@Override
			public String getMessage() {
				return "starting event";
			}
		});
	}

}
