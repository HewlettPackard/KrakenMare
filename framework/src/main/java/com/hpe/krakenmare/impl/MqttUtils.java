package com.hpe.krakenmare.impl;

import java.util.UUID;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.core.Agent;

public class MqttUtils {

	public static final UUID EMPTY_UUID = UUID.fromString("00000000-0000-0000-0000-000000000000");

	private static final String REGISTRATION_TOPIC = Main.getProperty("km.registration.mqtt.topic");
	private static final String SENSOR_LIST_TOPIC = Main.getProperty("km.device-registration.mqtt.topic");

	/* Registration */

	public static String getRegistrationRequestTopic() {
		return REGISTRATION_TOPIC + "/+/request";
	}

	// use "uid" here since the agent doesn't know yet its UUID so can't listen to it
	public static String getRegistrationRequestTopic(Agent agent) {
		return REGISTRATION_TOPIC + "/" + agent.getAgentUid() + "/request";
	}

	// use "uid" here since the agent doesn't know yet its UUID so can't listen to it
	public static String getRegistrationResponseTopic(Agent agent) {
		return getRegistrationResponseTopic(agent.getAgentUid());
	}

	// use "uid" here since the agent doesn't know yet its UUID so can't listen to it
	public static String getRegistrationResponseTopic(CharSequence uid) {
		return REGISTRATION_TOPIC + "/" + uid + "/response";
	}

	/* Sensor List */

	public static String getSensorListRequestTopic() {
		return SENSOR_LIST_TOPIC + "/+/request";
	}

	public static String getSensorListRequestTopic(Agent agent) {
		return SENSOR_LIST_TOPIC + "/" + agent.getAgentUuid() + "/request";
	}

	public static String getSensorListResponseTopic(Agent agent) {
		return getSensorListResponseTopic(agent.getAgentUuid());
	}

	public static String getSensorListResponseTopic(UUID uuid) {
		return SENSOR_LIST_TOPIC + "/" + uuid + "/response";
	}

}
