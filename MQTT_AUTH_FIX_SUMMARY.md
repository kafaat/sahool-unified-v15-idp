# MQTT Authentication Fix Summary

## Problem
MQTT broker was rejecting all client connections with "not authorised" errors:
- `sahool-iot-service-*` clients were repeatedly trying to connect and getting disconnected
- `auto-*` clients (from iot-gateway) were also being rejected
- Services were unable to connect to MQTT broker

## Root Cause
1. **Missing credentials in iot-service**: The TypeScript code in `iot-service` was not passing username and password to the MQTT connection, even though environment variables were set.
2. **Password mismatch**: The password hash in the `passwd` file may not have matched the environment variable password.

## Fixes Applied

### 1. Updated iot-service MQTT Connection (`apps/services/iot-service/src/iot/iot.service.ts`)
**Before:**
```typescript
this.client = mqtt.connect(brokerUrl, {
  clientId: `sahool-iot-service-${Date.now()}`,
  clean: true,
  connectTimeout: 4000,
  reconnectPeriod: 1000,
});
```

**After:**
```typescript
const username = process.env.MQTT_USER;
const password = process.env.MQTT_PASSWORD;

const connectOptions: mqtt.IClientOptions = {
  clientId: `sahool-iot-service-${Date.now()}`,
  clean: true,
  connectTimeout: 4000,
  reconnectPeriod: 1000,
};

// Add authentication if credentials are provided
if (username) {
  connectOptions.username = username;
}
if (password) {
  connectOptions.password = password;
}

this.client = mqtt.connect(brokerUrl, connectOptions);
```

**Impact:** The service now properly authenticates with the MQTT broker using the credentials from environment variables.

### 2. Regenerated MQTT Password File (`infrastructure/core/mqtt/passwd`)
Regenerated the password hash to ensure it matches the environment variable password:
- **Username:** `sahool_iot`
- **Password:** `change_this_secure_mqtt_password` (from environment variable)
- **New hash:** `$7$101$aNCf77HRKMVK8R/j$y8tjWmWmcwvoeGiCtHMB9SkzAFHN2FyopsE1MzDhdZnZ6QsESSdI2QnhNgHqpZWo9ovyFotfd3G7GAiKmYv+XA==`

**Impact:** Ensures the password hash in the passwd file matches what the services are using.

### 3. Rebuilt and Restarted Services
- Rebuilt `iot-service` container to apply code changes
- Restarted `iot-service`, `iot-gateway`, and `mqtt` containers

## Configuration Details

### Environment Variables (docker-compose.yml)
Both `iot-service` and `iot-gateway` have:
```yaml
- MQTT_USER=${MQTT_USER:-sahool_iot}
- MQTT_PASSWORD=${MQTT_PASSWORD}
```

### MQTT Broker Configuration
- **File:** `infrastructure/core/mqtt/mosquitto.conf`
- **Authentication:** `allow_anonymous false` (requires authentication)
- **Password file:** `/mosquitto/config/passwd`

### iot-gateway Status
The `iot-gateway` Python service already had correct authentication implementation:
```python
self._client = Client(
    hostname=self.broker,
    port=self.port,
    username=self.username if self.username else None,
    password=self.password if self.password else None,
)
```

## Expected Results

After these fixes:
- ✅ `iot-service` should successfully connect to MQTT broker with authentication
- ✅ `iot-gateway` should continue to work (was already correct)
- ✅ No more "not authorised" errors in MQTT logs
- ✅ Services can publish and subscribe to MQTT topics

## Verification

To verify the fixes are working:
```bash
# Check MQTT logs - should see successful connections
docker logs sahool-mqtt --tail 50 | grep -i "connect"

# Check iot-service logs - should see "Connected to MQTT Broker"
docker logs sahool-iot-service --tail 30 | grep -i "mqtt"

# Check for authentication errors (should be none)
docker logs sahool-mqtt --tail 100 | grep -i "not authorised"
```

## Files Modified

1. `apps/services/iot-service/src/iot/iot.service.ts` - Added username/password to MQTT connection
2. `infrastructure/core/mqtt/passwd` - Regenerated with correct password hash

## Next Steps

1. ✅ **Code fix applied** - Completed
2. ✅ **Password file updated** - Completed
3. ✅ **Services rebuilt and restarted** - Completed
4. ⏳ **Monitor logs** - Verify authentication is working
5. ⏳ **Test MQTT functionality** - Verify services can publish/subscribe

