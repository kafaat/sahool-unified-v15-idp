# WebSocket Authentication Implementation

## Overview

This document describes the WebSocket authentication implementation for the field-chat service. The `/ws/chat/{thread_id}` endpoint now includes comprehensive security measures.

## Implementation Details

### File Modified
- `/apps/services/field-chat/src/main.py`

### Security Features Implemented

#### 1. JWT Token Validation
- **Token Extraction**: Supports token from both query parameter and `Sec-WebSocket-Protocol` header
- **Validation**: Uses shared JWT module (`shared.security.jwt`) for token verification
- **Claims Required**: `sub` (user_id) and `tid` (tenant_id)
- **Revocation Check**: Automatically checks if token has been revoked

#### 2. Thread Access Verification
- **Participant Check**: Verifies user is a participant in the requested thread
- **Tenant Validation**: Ensures thread belongs to user's tenant
- **Archive Check**: Prevents connections to archived threads
- **Database Query**: Uses ChatRepository to verify access

#### 3. Rate Limiting
- **Message Limits**: 30 messages per minute per connection
- **Burst Protection**: Maximum 10 messages per second
- **Sliding Window**: Uses time-based sliding window algorithm
- **Per-Connection**: Rate limits tracked individually per WebSocket connection
- **Cleanup**: Automatically removes rate limit data on disconnect

### Code Structure

#### New Classes

**WebSocketRateLimiter**
```python
class WebSocketRateLimiter:
    """Rate limiter for WebSocket messages"""

    def __init__(self, messages_per_minute: int = 30, burst_limit: int = 10)
    def check_rate_limit(self, connection_id: str) -> tuple[bool, Optional[str]]
    def cleanup(self, connection_id: str)
```

#### New Functions

**validate_websocket_token(token: str) -> dict**
- Validates JWT token
- Returns decoded payload
- Raises ValueError on invalid token

**verify_thread_access(thread_id: UUID, tenant_id: str, user_id: str) -> tuple[bool, Optional[str]]**
- Checks if user is participant in thread
- Verifies tenant ownership
- Checks if thread is archived
- Returns (has_access, error_message)

### WebSocket Endpoint Behavior

#### Connection Flow

1. **Token Extraction**
   - First checks query parameter: `?token=<JWT>`
   - Falls back to `Sec-WebSocket-Protocol` header
   - Closes connection with code 4001 if no token

2. **Token Validation**
   - Verifies JWT signature and expiration
   - Extracts user_id and tenant_id from claims
   - Closes with code 4001 on invalid token

3. **Thread Access Check**
   - Validates thread_id format (UUID)
   - Queries database for thread and participant
   - Closes with code 4003 on access denied

4. **Connection Accepted**
   - Adds to connection manager
   - Sends confirmation message
   - Starts message loop

5. **Message Loop**
   - Applies rate limiting to each message
   - Handles ping/pong for keep-alive
   - Sends error on rate limit exceeded (doesn't disconnect)

6. **Cleanup**
   - Removes from connection manager
   - Clears rate limit data
   - Logs disconnection

#### WebSocket Close Codes

- **4000**: Invalid thread ID format
- **4001**: Authentication required or failed
- **4003**: Access denied (not a participant)

### Usage Examples

#### JavaScript/TypeScript Client

```javascript
// Get JWT token from your auth system
const token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...";
const threadId = "550e8400-e29b-41d4-a716-446655440000";

// Method 1: Token in query parameter (recommended)
const ws = new WebSocket(
  `ws://localhost:8000/ws/chat/${threadId}?token=${token}`
);

// Method 2: Token in Sec-WebSocket-Protocol header
const ws = new WebSocket(
  `ws://localhost:8000/ws/chat/${threadId}`,
  ["Bearer", token]
);

ws.onopen = () => {
  console.log("Connected to chat");
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "connected") {
    console.log("Authentication successful:", data);
  } else if (data.type === "error") {
    console.error("Error:", data.message);
  } else if (data.type === "pong") {
    console.log("Pong received");
  }
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = (event) => {
  console.log(`Connection closed: ${event.code} - ${event.reason}`);
};

// Send ping for keep-alive
setInterval(() => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send("ping");
  }
}, 30000); // Every 30 seconds
```

#### Python Client

```python
import asyncio
import websockets
import json

async def connect_to_chat():
    token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
    thread_id = "550e8400-e29b-41d4-a716-446655440000"

    uri = f"ws://localhost:8000/ws/chat/{thread_id}?token={token}"

    async with websockets.connect(uri) as websocket:
        # Wait for connection confirmation
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Connected: {data}")

        # Send messages
        await websocket.send("ping")
        pong = await websocket.recv()
        print(f"Pong: {pong}")

asyncio.run(connect_to_chat())
```

#### curl/websocat Test

```bash
# Install websocat: https://github.com/vi/websocat
TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
THREAD_ID="550e8400-e29b-41d4-a716-446655440000"

websocat "ws://localhost:8000/ws/chat/${THREAD_ID}?token=${TOKEN}"
```

### Response Messages

#### Connection Confirmation
```json
{
  "type": "connected",
  "thread_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user123",
  "message": "Connected to chat thread",
  "message_ar": "تم الاتصال بمحادثة الحقل"
}
```

#### Pong Response
```json
{
  "type": "pong",
  "timestamp": 1703001234.567
}
```

#### Rate Limit Error
```json
{
  "type": "error",
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Too many messages per minute.",
  "message_ar": "تم تجاوز حد الرسائل. يرجى الإبطاء."
}
```

#### Acknowledgment
```json
{
  "type": "ack",
  "received": "your message",
  "timestamp": 1703001234.567
}
```

## Security Considerations

### Implemented Security Measures

1. **Authentication**
   - JWT token required for all connections
   - Token signature verification
   - Expiration checking
   - Revocation support

2. **Authorization**
   - User must be participant in thread
   - Tenant isolation enforced
   - Archive status checked

3. **Rate Limiting**
   - Prevents message spam
   - Protects against DoS attacks
   - Per-connection tracking

4. **Logging**
   - All authentication attempts logged
   - Access denials logged with reasons
   - Rate limit violations logged
   - Connection lifecycle logged

### Best Practices

1. **Token Management**
   - Use short-lived access tokens (30 minutes default)
   - Implement token refresh mechanism
   - Don't expose tokens in URLs (use POST for REST, query param is OK for WS)
   - Store tokens securely (httpOnly cookies, secure storage)

2. **Connection Management**
   - Implement reconnection logic with exponential backoff
   - Handle network interruptions gracefully
   - Close connections properly on logout
   - Monitor connection health with ping/pong

3. **Error Handling**
   - Parse close codes to determine failure reason
   - Show user-friendly error messages
   - Log errors for debugging
   - Don't expose sensitive information in errors

4. **Rate Limiting**
   - Implement client-side throttling
   - Queue messages if rate limited
   - Show user feedback on rate limits
   - Don't retry too aggressively

## Testing

### Manual Testing

1. **Valid Connection**
```bash
# Get a valid token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq -r '.access_token')

# Connect to WebSocket
websocat "ws://localhost:8000/ws/chat/550e8400-e29b-41d4-a716-446655440000?token=${TOKEN}"
```

2. **No Token (Should Fail)**
```bash
websocat "ws://localhost:8000/ws/chat/550e8400-e29b-41d4-a716-446655440000"
# Expected: Connection closed with code 4001
```

3. **Invalid Token (Should Fail)**
```bash
websocat "ws://localhost:8000/ws/chat/550e8400-e29b-41d4-a716-446655440000?token=invalid"
# Expected: Connection closed with code 4001
```

4. **Not a Participant (Should Fail)**
```bash
# Use token from different user who is not a participant
websocat "ws://localhost:8000/ws/chat/550e8400-e29b-41d4-a716-446655440000?token=${OTHER_USER_TOKEN}"
# Expected: Connection closed with code 4003
```

5. **Rate Limit Test**
```bash
# Send many messages rapidly
for i in {1..50}; do echo "message $i"; done | \
  websocat "ws://localhost:8000/ws/chat/550e8400-e29b-41d4-a716-446655440000?token=${TOKEN}"
# Expected: Rate limit error after ~30 messages
```

### Integration Tests

See `/apps/services/field-chat/tests/test_websocket_auth.py` for automated tests.

## Migration Notes

### Breaking Changes

⚠️ **BREAKING**: WebSocket endpoint now requires authentication

- **Before**: Anonymous connections allowed
- **After**: JWT token required via query parameter or header

### Migration Path

1. Update all WebSocket clients to include JWT token
2. Ensure users are added as participants before connecting
3. Update client libraries to handle authentication errors
4. Test thoroughly in staging environment

### Backward Compatibility

None - this is a security fix and cannot be made backward compatible.

## Performance Considerations

### Memory Usage

- **Rate Limiter**: O(connections × messages_per_minute) timestamps stored
- **Cleanup**: Automatic cleanup on disconnect
- **Typical Load**: ~10KB per 1000 concurrent connections

### Database Queries

Each connection performs:
1. Thread lookup (indexed by ID and tenant_id)
2. Participant lookup (indexed by thread_id and user_id)

These are fast indexed queries with minimal overhead.

### Recommendations

- Use connection pooling for database
- Monitor active connection count
- Set reasonable WebSocket timeout (default: 60 seconds)
- Use Redis for rate limiting in production (future enhancement)

## Future Enhancements

1. **Redis-based Rate Limiting**
   - Distributed rate limiting across instances
   - Persistent rate limit state
   - More sophisticated algorithms

2. **Room-based Broadcasting**
   - Broadcast messages to all participants
   - Typing indicators
   - Read receipts

3. **Message Persistence**
   - Store WebSocket messages to database
   - Message history retrieval
   - Offline message delivery

4. **Advanced Security**
   - IP-based rate limiting
   - Geographic restrictions
   - Anomaly detection

## Troubleshooting

### Connection Rejected with Code 4001

**Cause**: Missing or invalid JWT token

**Solutions**:
- Verify token is included in request
- Check token expiration
- Verify token signature matches server key
- Check JWT_SECRET_KEY environment variable

### Connection Rejected with Code 4003

**Cause**: User is not a participant in the thread

**Solutions**:
- Add user as participant via POST `/chat/threads/{thread_id}/participants`
- Verify correct thread_id is being used
- Check tenant_id matches between token and thread

### Rate Limit Errors

**Cause**: Too many messages sent too quickly

**Solutions**:
- Implement client-side message queuing
- Reduce message frequency
- Check for message loops in client code

### Connection Closes Unexpectedly

**Cause**: Various (token expiration, network issues, server restart)

**Solutions**:
- Implement reconnection logic
- Check server logs for errors
- Monitor network connectivity
- Implement token refresh before expiration

## Support

For issues or questions:
- Check server logs: `/var/log/field-chat/`
- Review FastAPI docs: https://fastapi.tiangolo.com/advanced/websockets/
- Contact: platform-team@sahool.io
