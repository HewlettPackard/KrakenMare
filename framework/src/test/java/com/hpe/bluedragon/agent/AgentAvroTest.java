package com.hpe.bluedragon.agent;

import java.io.File;
import java.io.IOException;

import org.apache.avro.Conversions.UUIDConversion;
import org.apache.avro.Schema;
import org.apache.avro.compiler.specific.SpecificCompiler;
import org.junit.jupiter.api.Test;

public class AgentAvroTest {

	// static final UUID THE_UUID = UUID.fromString("12345678-abcd-dcba-1234-000000000000");
	// static final Agent THE_AGENT = new Agent(42l, THE_UUID.toString(), "myAgent");
	// static final String THE_JSON = "{\"id\":42,\"uuid\":\"12345678-abcd-dcba-1234-000000000000\",\"name\":\"myAgent\"}";
	//
	// @Test
	// void testJSonSer() throws IOException {
	// DatumWriter<Agent> writer = new SpecificDatumWriter<>(Agent.class);
	// ByteArrayOutputStream stream = new ByteArrayOutputStream();
	// Encoder encoder = EncoderFactory.get().jsonEncoder(Agent.getClassSchema(), stream, /* pretty */false);
	// writer.write(THE_AGENT, encoder);
	// encoder.flush();
	// byte[] data = stream.toByteArray();
	//
	// assertEquals(THE_JSON, new String(data));
	// }
	//
	// @Test
	// void testAvroFileSerDe() throws IOException {
	// File file = new File("/tmp/agent-avro-test.ser");
	//
	// DatumWriter<Agent> writer = new SpecificDatumWriter<>(Agent.class);
	// DataFileWriter<Agent> dataFileWriter = new DataFileWriter<>(writer);
	// dataFileWriter.create(THE_AGENT.getSchema(), file);
	// dataFileWriter.append(THE_AGENT);
	// dataFileWriter.close();
	//
	// DatumReader<Agent> userDatumReader = new SpecificDatumReader<>(Agent.class);
	// try (DataFileReader<Agent> dataFileReader = new DataFileReader<>(file, userDatumReader)) {
	// Agent agent = null;
	// while (dataFileReader.hasNext()) {
	// // Reuse user object by passing it to next(). This saves us from
	// // allocating and garbage collecting many objects for files with
	// // many items.
	// agent = dataFileReader.next(agent);
	// assertEquals(THE_AGENT, agent);
	// }
	// }
	// }
	//
	// @Test
	// void testAvroBytesSerDe() throws IOException {
	// ByteBuffer buffer = THE_AGENT.toByteBuffer();
	// Agent agent = Agent.fromByteBuffer(buffer);
	// assertEquals(THE_AGENT, agent);
	// }

	@Test
	void testCompile() throws IOException {
		File src = new File("/home/poulainc/workspace_pathforward/wp1.3/framework/src/main/avro/", "agent.avsc");
		Schema schema = new Schema.Parser().parse(src);

		SpecificCompiler compiler = new SpecificCompiler(schema);
		compiler.addCustomConversion(UUIDConversion.class);
		// compiler.setTemplateDir("/home/poulainc/workspace_pathforward/wp1.3/framework/src/main/resources/velocity-templates/");
		compiler.compileToDestination(src, new File("/tmp/"));
	}

}
