package com.hpe.krakenmare;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.util.Properties;

import org.eclipse.paho.client.mqttv3.MqttException;
import org.glassfish.grizzly.http.server.HttpServer;
import org.glassfish.hk2.utilities.binding.AbstractBinder;
import org.glassfish.jersey.grizzly2.httpserver.GrizzlyHttpServerFactory;
import org.glassfish.jersey.jackson.JacksonFeature;
import org.glassfish.jersey.server.ResourceConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Framework;
import com.hpe.krakenmare.impl.FrameworkImpl;

public class Main {

	public final static Logger LOG = LoggerFactory.getLogger(Main.class);

	private final static Properties PROPERTIES = new Properties();
	static {
		ClassLoader classloader = Thread.currentThread().getContextClassLoader();
		try (InputStream input = classloader.getResourceAsStream("config.properties")) {
			PROPERTIES.load(input);
		} catch (IOException e) {
			LOG.error("Unable to load properties", e);
		}

		// override with env parameters and then with command line (-Dxxxx=yyyy) parameters
		for (Object key : PROPERTIES.keySet()) {
			if (key instanceof String) {
				String keyStr = (String) key;

				String envKey = keyStr.replace(".", "_").toUpperCase();
				String value = System.getenv(envKey);
				if (value != null) {
					PROPERTIES.put(keyStr, value);
				}

				value = System.getProperty(keyStr);
				if (value != null) {
					PROPERTIES.put(keyStr, value);
				}
			}
		}
	}

	public static Properties cloneProperties() {
		return (Properties) PROPERTIES.clone();
	}

	public static String getProperty(String key) {
		return PROPERTIES.getProperty(key);
	}

	static class App extends ResourceConfig {

		public App(final FrameworkImpl framework) {
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

	public static void main(String[] args) throws IOException, InterruptedException, MqttException {
		LOG.info("Starting framework...");
		final FrameworkImpl framework = new FrameworkImpl();
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
