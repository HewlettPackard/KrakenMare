package com.hpe.bluedragon.repositories;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.github.fppt.jedismock.RedisServer;
import com.hpe.bluedragon.core.Agent;

import redis.clients.jedis.Jedis;

public class AgentRedisRepositoryTest {

	private static RedisServer server = null;
	private static AgentRedisRepository repo = null;

	@BeforeEach
	void before() throws IOException {
		server = RedisServer.newRedisServer(); // bind to a random port
		server.start();

		// Jedis jedis = new Jedis(HostAndPort.parseString(Main.PROPERTIES.getProperty("redis.server")));
		Jedis jedis = new Jedis(server.getHost(), server.getBindPort());
		repo = new AgentRedisRepository(jedis);
	}

	@AfterEach
	void after() {
		server.stop();
		server = null;
		repo = null;
	}

	@Test
	void testAdd() {
		Agent agent = repo.create("myAgent");
		assertTrue(repo.save(agent));
		assertEquals(1, repo.getAll().size());
	}

	@Test
	void testDelete() {
		Agent agent1 = repo.create("myAgent1");
		assertTrue(repo.save(agent1));
		Agent agent2 = repo.create("myAgent2");
		assertTrue(repo.save(agent2));
		Agent agent3 = repo.create("myAgent3");
		assertTrue(repo.save(agent3));
		assertEquals(3, repo.getAll().size());

		assertTrue(repo.delete(agent2));
		assertEquals(2, repo.getAll().size());

		assertTrue(repo.delete(agent1));
		assertEquals(1, repo.getAll().size());
	}

}
