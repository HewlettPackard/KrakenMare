FROM eclipse-mosquitto:1.6.9

COPY mosquitto.conf /mosquitto/config/mosquitto.conf
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
