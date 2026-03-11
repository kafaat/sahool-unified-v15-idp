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
# Strip \r (Windows line endings) to ensure sed patterns match correctly on all platforms
sed 's|acl_file /mosquitto/config/acl.source|acl_file /mosquitto/config/acl|' /mosquitto/config/mosquitto.conf.orig | tr -d '\r' > /mosquitto/config/mosquitto.conf

# Remove TLS listener blocks if certificate files are not present
# This allows development environments to run without TLS certificates
if [ ! -f /mosquitto/certs/ca.crt ] || [ ! -f /mosquitto/certs/server.crt ] || [ ! -f /mosquitto/certs/server.key ]; then
    echo "NOTICE: TLS certificates not found at /mosquitto/certs/ - disabling TLS listeners (8883, 9443)"
    # Remove TLS listener blocks (from "listener 8883" through the next blank line, and same for 9443)
    sed -i '/^listener 8883$/,/^$/d; /^listener 9443$/,/^$/d' /mosquitto/config/mosquitto.conf
fi

# Start mosquitto - it will drop privileges to mosquitto user
exec /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
