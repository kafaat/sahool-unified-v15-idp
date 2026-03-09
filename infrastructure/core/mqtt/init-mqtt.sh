#!/bin/sh
set -e

# Ensure /mosquitto/config directory exists and is writable
mkdir -p /mosquitto/config
chmod 755 /mosquitto/config

# Create passwd file - owned by mosquitto user (required for Mosquitto to read it after dropping privileges)
# NOTE: Future Mosquitto versions may require root:root, but current version needs mosquitto ownership
# Remove existing passwd file if it exists (from previous runs)
rm -f /mosquitto/config/passwd
mosquitto_passwd -b -c /mosquitto/config/passwd "${MQTT_USER}" "${MQTT_PASSWORD}" || {
    echo "ERROR: Failed to create passwd file" >&2
    exit 1
}
chown mosquitto:mosquitto /mosquitto/config/passwd
chmod 600 /mosquitto/config/passwd

# Create per-service MQTT users (append to existing passwd file)
# Uses -b flag (batch mode) without -c flag (to append, not overwrite)
if [ -n "${MQTT_IOT_GATEWAY_PASSWORD:-}" ]; then
    mosquitto_passwd -b /mosquitto/config/passwd iot_gateway "${MQTT_IOT_GATEWAY_PASSWORD}"
fi
if [ -n "${MQTT_SENSOR_HUB_PASSWORD:-}" ]; then
    mosquitto_passwd -b /mosquitto/config/passwd iot_sensor_hub "${MQTT_SENSOR_HUB_PASSWORD}"
fi
if [ -n "${MQTT_EDGE_PASSWORD:-}" ]; then
    mosquitto_passwd -b /mosquitto/config/passwd edge_orchestrator "${MQTT_EDGE_PASSWORD}"
fi
if [ -n "${MQTT_IRRIGATION_PASSWORD:-}" ]; then
    mosquitto_passwd -b /mosquitto/config/passwd irrigation_smart "${MQTT_IRRIGATION_PASSWORD}"
fi

# Re-apply permissions after adding users
chown mosquitto:mosquitto /mosquitto/config/passwd
chmod 600 /mosquitto/config/passwd

# Copy ACL file from read-only mount to writable location with correct ownership
rm -f /mosquitto/config/acl
cp /mosquitto/config/acl.source /mosquitto/config/acl
chown mosquitto:mosquitto /mosquitto/config/acl
chmod 600 /mosquitto/config/acl

# Create modified mosquitto.conf that points to the fixed ACL file
sed 's|acl_file /mosquitto/config/acl.source|acl_file /mosquitto/config/acl|' /mosquitto/config/mosquitto.conf.orig > /mosquitto/config/mosquitto.conf

# Start mosquitto - it will drop privileges to mosquitto user
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
