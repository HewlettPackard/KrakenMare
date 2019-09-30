package com.hpe.krakenmare.impl;

import com.hpe.krakenmare.Main;
import com.hpe.krakenmare.core.Agent;

public class MqttUtils {

	private static final String REGISTRATION_TOPIC = Main.getProperty("km.registration.mqtt.topic");

	public static String getRegistrationRequestTopic() {
		return REGISTRATION_TOPIC + "/+/request";
	}

	// use "uid" here since the agent doesn't know yet its UUID so can't listen to it
	public static String getRegistrationRequestTopic(Agent agent) {
		return REGISTRATION_TOPIC + "/" + agent.getUid() + "/request";
	}

	public static String getRegistrationResponseTopic(Agent agent) {
		return REGISTRATION_TOPIC + "/" + agent.getUid() + "/response";
	}

}
