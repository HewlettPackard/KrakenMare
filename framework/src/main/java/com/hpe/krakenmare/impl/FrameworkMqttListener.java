package com.hpe.krakenmare.impl;

import java.io.IOException;
import java.nio.ByteBuffer;

import org.apache.avro.specific.SpecificRecordBase;
import org.eclipse.paho.client.mqttv3.IMqttClient;
import org.eclipse.paho.client.mqttv3.IMqttMessageListener;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.hpe.krakenmare.api.Repository;
import com.hpe.krakenmare.core.Agent;

public abstract class FrameworkMqttListener<P extends SpecificRecordBase, R extends SpecificRecordBase> implements IMqttMessageListener {

	final static Logger LOG = LoggerFactory.getLogger(FrameworkMqttListener.class);

	protected final Repository<Agent> repository;
	protected final IMqttClient mqtt;

	public FrameworkMqttListener(Repository<Agent> repository, IMqttClient mqtt) {
		this.repository = repository;
		this.mqtt = mqtt;
	}

	@Override
	public void messageArrived(String topic, MqttMessage message) {
		LOG.info("Message received on topic '" + topic + "': " + message);
		try {
			P payload = fromByteBuffer(ByteBuffer.wrap(message.getPayload()));
			R response = process(payload);
			afterProcess(payload, response);
		} catch (Exception e) {
			LOG.error("Exception occured during message handling", e);
		}
	}

	abstract P fromByteBuffer(ByteBuffer b) throws IOException;

	abstract R process(P payload);

	abstract void afterProcess(P payload, R response) throws Exception;

}
