package com.hpe.krakenmare.agent;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.UUID;

import org.apache.avro.Conversions.UUIDConversion;
import org.apache.avro.Schema;
import org.apache.avro.compiler.specific.SpecificCompiler;
import org.apache.avro.file.DataFileReader;
import org.apache.avro.file.DataFileWriter;
import org.apache.avro.io.DatumReader;
import org.apache.avro.io.DatumWriter;
import org.apache.avro.io.Encoder;
import org.apache.avro.io.EncoderFactory;
import org.apache.avro.specific.SpecificDatumReader;
import org.apache.avro.specific.SpecificDatumWriter;
import org.apache.avro.util.Utf8;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

import com.hpe.krakenmare.core.Agent;

public class AgentAvroTest {

	static final UUID THE_UUID = UUID.fromString("12345678-abcd-dcba-1234-000000000000");
	static final Agent THE_AGENT = new Agent(42l, new Utf8("agent-42"), THE_UUID, new Utf8("myAgent"), Collections.emptyList());
	static final String THE_JSON = "{\"agentId\":42,\"agentUid\":\"agent-42\",\"agentUuid\":\"12345678-abcd-dcba-1234-000000000000\",\"agentName\":\"myAgent\",\"devices\":[]}";

	@Test
	void testJSonSer() throws IOException {
		DatumWriter<Agent> writer = new SpecificDatumWriter<>(Agent.class);
		ByteArrayOutputStream stream = new ByteArrayOutputStream();
		Encoder encoder = EncoderFactory.get().jsonEncoder(Agent.getClassSchema(), stream, /* pretty */false);
		writer.write(THE_AGENT, encoder);
		encoder.flush();
		byte[] data = stream.toByteArray();

		assertEquals(THE_JSON, new String(data));
	}

	@Test
	void testAvroFileSerDe() throws IOException {
		File file = new File("/tmp/agent-avro-test.ser");

		DatumWriter<Agent> writer = new SpecificDatumWriter<>(Agent.class);
		DataFileWriter<Agent> dataFileWriter = new DataFileWriter<>(writer);
		dataFileWriter.create(THE_AGENT.getSchema(), file);
		dataFileWriter.append(THE_AGENT);
		dataFileWriter.close();

		DatumReader<Agent> userDatumReader = new SpecificDatumReader<>(Agent.class);
		try (DataFileReader<Agent> dataFileReader = new DataFileReader<>(file, userDatumReader)) {
			Agent agent = null;
			while (dataFileReader.hasNext()) {
				// Reuse user object by passing it to next(). This saves us from
				// allocating and garbage collecting many objects for files with
				// many items.
				agent = dataFileReader.next(agent);
				assertEquals(THE_AGENT, agent);
			}
		}
	}

	@Test
	void testAvroBytesSerDe() throws IOException {
		ByteBuffer buffer = THE_AGENT.toByteBuffer();
		Agent agent = Agent.fromByteBuffer(buffer);
		assertEquals(THE_AGENT, agent);
	}

	@Test
	@Disabled("Use to test Avro code generation as done by mvn plugin")
	void testCompile() throws IOException {
		File src = new File("src/main/avro/", "agent.avsc");
		Schema schema = new Schema.Parser().parse(src);

		SpecificCompiler compiler = new SpecificCompiler(schema);
		compiler.addCustomConversion(UUIDConversion.class);
		compiler.setTemplateDir("src/main/resources/velocity-templates/");
		compiler.compileToDestination(src, new File("/tmp/"));
	}

}
