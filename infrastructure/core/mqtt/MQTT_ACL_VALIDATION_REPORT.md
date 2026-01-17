# MQTT ACL Validation Report

## SAHOOL Unified IDP - MQTT Access Control List

---

## Executive Summary

The MQTT ACL configuration has been analyzed for correctness, consistency, and alignment with actual system usage patterns. This report documents findings, issues, and recommendations.

**Overall Status:** ✓ FUNCTIONAL WITH NOTABLE ISSUES

---

## 1. CONFIGURATION STRUCTURE ANALYSIS

### 1.1 Format Compliance

- **Status:** ✓ VALID
- **Findings:**
  - Syntax follows Mosquitto ACL standard correctly
  - Comments are properly formatted
  - User and topic declarations are clear
  - All required wildcard patterns are documented

### 1.2 User Permissions Defined

#### Users Configured:

```
✓ admin         - Full access (readwrite #)
✓ sahool_iot    - IoT service with granular permissions
✓ test_sensor   - Test/development user
✓ simulator     - Simulation environment user
✓ monitor       - Read-only monitoring user
```

---

## 2. TOPIC PATTERN VALIDATION

### 2.1 Actual Topic Patterns Found in Codebase

#### Primary Topic Structure (Production):

```
sahool/{tenantId}/farm/{farmId}/field/{fieldId}/sensor/{sensorType}
sahool/{tenantId}/farm/{farmId}/field/{fieldId}/actuator/{actuatorType}/command
sahool/{tenantId}/farm/{farmId}/field/{fieldId}/actuator/{actuatorType}/{id}/command
sahool/{tenantId}/farm/{farmId}/field/{fieldId}/irrigation/schedule
sahool/{tenantId}/farm/{farmId}/device/status
```

#### Load Test Patterns (Alternative):

```
sahool/iot/soil/{region}/{deviceId}
sahool/iot/weather/{region}/{deviceId}
sahool/iot/irrigation/{region}/{deviceId}/status
sahool/iot/gps/{region}/{deviceId}
```

#### System & Test Patterns:

```
sahool/system/#
sahool/test/#
sahool/simulation/#
$SYS/#
```

### 2.2 ACL Coverage Analysis

| Topic Pattern                                      | ACL Rule                                                       | Coverage  | Status |
| -------------------------------------------------- | -------------------------------------------------------------- | --------- | ------ |
| `sahool/+/farm/+/field/+/sensor/#`                 | `topic read sahool/+/farm/+/field/+/sensor/#`                  | ✓ Full    | OK     |
| `sahool/sensors/#`                                 | `topic read sahool/sensors/#`                                  | ✓ Full    | OK     |
| `sahool/+/farm/+/field/+/actuator/#`               | `topic read sahool/+/farm/+/field/+/actuator/#`                | ✓ Full    | OK     |
| `sahool/+/farm/+/device/status`                    | `topic read sahool/+/farm/+/device/status`                     | ✓ Full    | OK     |
| `sahool/+/farm/+/field/+/actuator/+/command`       | `topic write sahool/+/farm/+/field/+/actuator/+/command`       | ✓ Full    | OK     |
| `sahool/+/farm/+/field/+/actuator/pump/command`    | `topic write sahool/+/farm/+/field/+/actuator/pump/command`    | ✓ Full    | OK     |
| `sahool/+/farm/+/field/+/actuator/valve/+/command` | `topic write sahool/+/farm/+/field/+/actuator/valve/+/command` | ✓ Full    | OK     |
| `sahool/+/farm/+/field/+/irrigation/schedule`      | `topic write sahool/+/farm/+/field/+/irrigation/schedule`      | ✓ Full    | OK     |
| `sahool/system/#`                                  | `topic readwrite sahool/system/#`                              | ✓ Full    | OK     |
| `sahool/iot/*` (load test)                         | NOT EXPLICITLY COVERED                                         | ✗ Partial | ISSUE  |
| `$SYS/#`                                           | `topic read $SYS/#` (monitor user)                             | ✓ Full    | OK     |

---

## 3. PERMISSION ANALYSIS

### 3.1 sahool_iot User Permissions

#### READ Permissions:

```
✓ sahool/+/farm/+/field/+/sensor/#        - Sensors from any farm/field
✓ sahool/sensors/#                        - Generic sensor topic
✓ sahool/+/farm/+/field/+/actuator/#      - Actuator status/feedback
✓ sahool/+/farm/+/device/status           - Device health data
✓ sahool/system/#                         - System topics
```

**Assessment:** ✓ CORRECT

- Allows reading from all required sensor and status topics
- Follows principle of least privilege
- Appropriately scoped by tenant/farm/field hierarchy

#### WRITE Permissions:

```
✓ sahool/+/farm/+/field/+/actuator/+/command          - Generic actuator commands
✓ sahool/+/farm/+/field/+/actuator/pump/command       - Pump control
✓ sahool/+/farm/+/field/+/actuator/valve/+/command    - Valve control
✓ sahool/+/farm/+/field/+/irrigation/schedule         - Irrigation scheduling
✓ sahool/system/#                                      - System state changes
```

**Assessment:** ✓ CORRECT

- Provides required actuator control capabilities
- Appropriately restricted to command topics
- Does not allow publishing to sensor/status topics

### 3.2 Semantic Correctness of Read/Write Permissions

| User        | Topic               | Direction  | Semantics                               | Status    |
| ----------- | ------------------- | ---------- | --------------------------------------- | --------- |
| sahool_iot  | sensor/#            | READ       | Service reads sensor data               | ✓ Correct |
| sahool_iot  | actuator/#          | READ       | Service subscribes to actuator feedback | ✓ Correct |
| sahool_iot  | actuator/command    | WRITE      | Service sends control commands          | ✓ Correct |
| sahool_iot  | irrigation/schedule | WRITE      | Service publishes schedules             | ✓ Correct |
| test_sensor | sahool/test/#       | READ/WRITE | Test device can pub/sub test topics     | ✓ Correct |
| simulator   | sahool/sensors/#    | WRITE      | Simulator publishes fake data           | ✓ Correct |
| monitor     | sahool/#            | READ       | Monitor observes system                 | ✓ Correct |
| monitor     | $SYS/#              | READ       | Monitor sees broker stats               | ✓ Correct |

---

## 4. ISSUES IDENTIFIED

### Issue #1: Load Test Topic Pattern Not Covered

**Severity:** MEDIUM
**Location:** ACL line 68 (simulator user)

The load test script uses topic pattern:

```
sahool/iot/soil/{region}/{deviceId}
sahool/iot/weather/{region}/{deviceId}
sahool/iot/irrigation/{region}/{deviceId}/status
sahool/iot/gps/{region}/{deviceId}
```

But the ACL only covers:

```
topic readwrite sahool/simulation/#
topic write sahool/sensors/#
```

**Impact:** Load test may fail to publish to intended topics

**Recommendation:**
Add to simulator user:

```
# Load test IoT device patterns
topic write sahool/iot/soil/#
topic write sahool/iot/weather/#
topic write sahool/iot/irrigation/#
topic write sahool/iot/gps/#
```

### Issue #2: Inconsistent Topic Namespace

**Severity:** MEDIUM
**Location:** Multiple files

Found three different naming conventions in codebase:

1. Production: `sahool/{tenant}/farm/{farm}/field/{field}/...`
2. Load test: `sahool/iot/{type}/{region}/{deviceId}`
3. Load test prefix variable: `sahool/iot` (from mqtt-iot-simulation.js)

**Impact:** Potential confusion, topic sprawl, harder to manage permissions

**Recommendation:**

- Standardize on primary namespace: `sahool/{tenant}/farm/{farm}/field/{field}/`
- Move IoT simulation to use same namespace with `test/` or `simulation/` tenant ID
- Document any legacy topics

### Issue #3: Device Authentication via Pattern

**Severity:** LOW
**Location:** ACL line 54-57 (commented out)

Device-specific user pattern is commented out:

```
# user sensor_device_001
# topic write sahool/+/farm/+/field/+/sensor/#
# topic read sahool/+/farm/+/field/+/actuator/+/command
```

**Impact:** Each physical device cannot authenticate individually - all devices share sahool_iot credentials

**Recommendation:**

- Consider implementing device-specific authentication for production
- Use client certificate-based auth or per-device tokens
- At minimum, document this limitation

### Issue #4: Actuator Status Read Permission Ambiguity

**Severity:** LOW
**Location:** ACL line 35

Current rule:

```
topic read sahool/+/farm/+/field/+/actuator/#
```

This allows reading ALL actuator topics including command topics. More precise would be:

```
topic read sahool/+/farm/+/field/+/actuator/+/status
topic read sahool/+/farm/+/field/+/actuator/+/feedback
```

**Impact:** Minor - service can read own command topics (not a security issue)

**Recommendation:**

- Document that read on actuator/# includes command topics
- Consider splitting into explicit status/feedback topics

---

## 5. WILDCARD PATTERN ANALYSIS

### 5.1 Wildcard Usage Validation

| Pattern              | Type         | Validation | Status |
| -------------------- | ------------ | ---------- | ------ |
| `#`                  | Multi-level  | ✓ Valid    | OK     |
| `+`                  | Single-level | ✓ Valid    | OK     |
| `+/+/+/+/+/sensor/#` | Mixed        | ✓ Valid    | OK     |
| `$SYS/#`             | System topic | ✓ Valid    | OK     |

**Assessment:** ✓ ALL WILDCARD PATTERNS VALID

### 5.2 Wildcard Hierarchy Check

Subscriptions follow proper MQTT hierarchy:

- Topic levels separated by `/`
- Single-level wildcards (+) correctly replace one level
- Multi-level wildcard (#) only at end
- No wildcard misplacements

---

## 6. SECURITY ASSESSMENT

### 6.1 Principle of Least Privilege

**Status:** ✓ GOOD

- **admin**: Full access (expected for administrative use)
- **sahool_iot**: Limited to required operations
- **test_sensor**: Limited to test namespace
- **simulator**: Limited to simulation/sensors
- **monitor**: Read-only, no write permissions
- **Default**: Implicit deny for all other users

### 6.2 Topic Isolation

**Status:** ✓ GOOD

- Test topics isolated in `sahool/test/#`
- Simulation topics isolated in `sahool/simulation/#`
- Production topics use structured hierarchy
- System topics restricted to system user operations

### 6.3 Potential Vulnerabilities

#### Risk 1: Implicit Device Trust

- All IoT devices authenticate as `sahool_iot`
- Cannot distinguish between legitimate and compromised devices
- Mitigation: Implement per-device authentication in future

#### Risk 2: Wide Sensor Read Access

- sahool_iot can read from ALL sensor topics
- Cannot scope to specific farms/fields per device
- Current design assumes all data equally sensitive
- Mitigation: Document this limitation, use separate MQTT brokers for isolated environments

#### Risk 3: System Topic Access

- sahool_iot has readwrite access to sahool/system/#
- Should verify what system topics are used
- Mitigation: Audit and restrict specific system topics if not all needed

---

## 7. CONFIGURATION COMPLETENESS

### 7.1 Broker Settings Verification

**File:** `/home/user/sahool-unified-v15-idp/infrastructure/core/mqtt/mosquitto.conf`

- ✓ Anonymous access disabled: `allow_anonymous false`
- ✓ ACL file configured: `acl_file /mosquitto/config/acl`
- ✓ Password file configured: `password_file /mosquitto/config/passwd`
- ✓ Multiple listeners: MQTT (1883) + WebSockets (9001)
- ✓ Persistence enabled
- ✓ Connection limits set: 1000 max connections

**Status:** ✓ BROKER PROPERLY CONFIGURED

### 7.2 Docker Integration

**File:** `/home/user/sahool-unified-v15-idp/docker-compose.yml`

- ✓ ACL file mounted: `./infrastructure/core/mqtt/acl:/mosquitto/config/acl:ro`
- ✓ Read-only mount (security best practice)

**Status:** ✓ DOCKER INTEGRATION CORRECT

---

## 8. RECOMMENDATIONS SUMMARY

### Priority 1 (High) - Functional Issues

1. **Add load test topic patterns to ACL**
   - Add `topic write sahool/iot/#` to simulator user
   - Prevents load test failures

### Priority 2 (Medium) - Design Issues

2. **Standardize topic namespace**
   - Consolidate IoT patterns to use primary namespace
   - Document any legacy patterns
   - Simplifies ACL management

3. **Implement device-specific authentication**
   - Move from shared sahool_iot credentials to per-device auth
   - Use client certificates or token-based auth
   - Improves security and forensics

### Priority 3 (Low) - Documentation

4. **Document topic model assumptions**
   - Clarify multi-tenant data isolation approach
   - Document expected tenant IDs
   - Add examples of valid topic paths

5. **Audit system topic usage**
   - Verify which `sahool/system/#` topics are actually used
   - Restrict permissions to only required topics
   - Document system state management design

---

## 9. VALIDATION CHECKLIST

- [x] User permissions correctly defined
- [x] Topic patterns follow MQTT syntax rules
- [x] Read/write permissions make semantic sense
- [x] Wildcard patterns valid and properly used
- [x] Security: Principle of least privilege applied
- [x] Security: Default deny implemented
- [x] Broker configuration matches ACL
- [x] Docker mount configuration correct
- [x] Main production topics covered
- [ ] Load test topics fully covered ← ACTION NEEDED
- [x] Test/simulation topics isolated
- [ ] Device-specific authentication implemented (future)

---

## 10. CONCLUSION

**Overall Assessment: ACCEPTABLE WITH MINOR ISSUES**

The MQTT ACL configuration is properly structured and meets the security requirements for the current system. The primary concern is coverage of load test topics and the long-term need for per-device authentication.

**Immediate Actions Required:**

1. Add `sahool/iot/#` write permission to simulator user
2. Verify load test can publish to all intended topics

**Follow-up Actions:**

1. Implement per-device authentication strategy
2. Standardize topic namespace across all services
3. Audit and document system topic usage
4. Consider implementing broker-level tenant isolation

---

**Report Generated:** 2026-01-06
**Configuration File:** `/home/user/sahool-unified-v15-idp/infrastructure/core/mqtt/acl`
**Validation Tool:** Manual analysis with codebase review
