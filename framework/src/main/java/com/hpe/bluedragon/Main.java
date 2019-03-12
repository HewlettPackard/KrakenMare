package com.hpe.bluedragon;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.util.Properties;

import org.apache.kafka.streams.StreamsConfig;
import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.jackson.JacksonFeature;
import org.glassfish.jersey.server.ResourceConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.google.common.base.Strings;
import com.hpe.bluedragon.framework.Framework;

public class Main {

	public final static Logger LOG = LoggerFactory.getLogger(Main.class);

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

	static class App extends ResourceConfig {

		public App(final Framework framework) {
			packages(getClass().getPackage().getName());
			// dependencies injection
			register(new AbstractBinder() {
				@Override
				protected void configure() {
					bind(framework).to(Framework.class);
				}
			});
			// Jackson
			register(JacksonFeature.class);
		}

	}

	public static void main(String[] args) throws IOException, InterruptedException {
		LOG.info("Starting framework...");
		final Framework framework = new Framework();
		framework.startFramework();

		LOG.info("Starting web server...");
		final App app = new App(framework);
		final String baseUri = PROPERTIES.getProperty("application.baseUri");
		final HttpServer server = GrizzlyHttpServerFactory.createHttpServer(URI.create(baseUri), app);

		Runtime.getRuntime().addShutdownHook(new Thread() {
			@Override
			public void run() {
				LOG.info("Stopping web server...");
				server.shutdownNow();
				LOG.info("Stopping framework...");
				framework.stopFramework();
			}
		});
	}

}
