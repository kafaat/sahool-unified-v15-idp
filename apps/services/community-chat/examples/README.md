# Community Chat Service - Client Examples

# أمثلة عملاء خدمة الدردشة

## 📋 Overview / نظرة عامة

هذا المجلد يحتوي على أمثلة عملية لكيفية التكامل مع خدمة الدردشة الحية لسهول.

This folder contains practical examples of how to integrate with the Sahool Community Chat Service.

## 🚀 Getting Started / البدء

### 1. Install Dependencies / تثبيت المتطلبات

```bash
cd examples
npm install
```

### 2. Set Environment Variables / تعيين متغيرات البيئة

```bash
export JWT_TOKEN="your-valid-jwt-token"
export CHAT_SERVICE_URL="http://localhost:8097"
```

### 3. Run Examples / تشغيل الأمثلة

#### Farmer Example / مثال المزارع

```bash
npm run farmer
# or
node client-example.js farmer
```

This example demonstrates:

- Connecting as a farmer
- Requesting expert help
- Joining a support room
- Sending messages

#### Expert Example / مثال الخبير

```bash
npm run expert
# or
node client-example.js expert
```

This example demonstrates:

- Connecting as an expert
- Listening for support requests
- Accepting requests
- Joining consultation rooms

#### REST API Example / مثال REST API

```bash
npm run rest
# or
node client-example.js rest
```

This example demonstrates:

- Health check endpoint
- Getting online experts count
- Fetching support requests
- Retrieving room messages
- Getting service statistics

## 📝 Example Files / ملفات الأمثلة

### client-example.js

Contains a complete `ChatClient` class that can be used in your application:

```javascript
const { ChatClient } = require("./client-example");

// Create a client instance
const client = new ChatClient(
  jwtToken,
  userId,
  userName,
  userType,
  governorate,
);

// Connect
await client.connect();

// Join a room
await client.joinRoom(roomId);

// Send a message
client.sendMessage("Hello!");

// Disconnect
client.disconnect();
```

## 🔐 Authentication / المصادقة

All examples require a valid JWT token. The token should include:

جميع الأمثلة تتطلب توكن JWT صالح. يجب أن يحتوي التوكن على:

```json
{
  "sub": "user-id",
  "role": "farmer|expert|admin",
  "iat": 1735295400,
  "exp": 1735381800
}
```

You can generate a test token using the auth service or your JWT generation tool.

## 📡 Events Reference / مرجع الأحداث

### Client → Server

| Event            | Description              | Example            |
| ---------------- | ------------------------ | ------------------ |
| `register_user`  | Register user on connect | See farmer example |
| `join_room`      | Join a chat room         | See farmer example |
| `send_message`   | Send a message           | See farmer example |
| `typing_start`   | Start typing indicator   | See farmer example |
| `typing_stop`    | Stop typing indicator    | See farmer example |
| `request_expert` | Request expert help      | See farmer example |
| `accept_request` | Accept support request   | See expert example |
| `leave_room`     | Leave a room             | See farmer example |

### Server → Client

| Event                    | Description          | Handled In              |
| ------------------------ | -------------------- | ----------------------- |
| `registration_confirmed` | User registered      | `connect()`             |
| `load_history`           | Room message history | `joinRoom()`            |
| `receive_message`        | New message          | `setupEventListeners()` |
| `user_joined`            | User joined room     | `setupEventListeners()` |
| `user_left`              | User left room       | `setupEventListeners()` |
| `user_typing`            | Typing indicator     | `setupEventListeners()` |
| `expert_online`          | Expert came online   | `setupEventListeners()` |
| `expert_offline`         | Expert went offline  | `setupEventListeners()` |
| `new_support_request`    | New support request  | `setupEventListeners()` |
| `expert_joined`          | Expert joined room   | `setupEventListeners()` |
| `request_taken`          | Request was accepted | `setupEventListeners()` |
| `error`                  | Error notification   | `setupEventListeners()` |

## 🧪 Testing / الاختبار

### Manual Testing / الاختبار اليدوي

1. Start the chat service:

   ```bash
   cd ..
   npm start
   ```

2. In another terminal, run the farmer example:

   ```bash
   cd examples
   npm run farmer
   ```

3. In another terminal, run the expert example:

   ```bash
   cd examples
   npm run expert
   ```

4. Watch the console output to see the real-time interaction

### Testing with Postman

1. Import the OpenAPI spec from `http://localhost:8097/api-docs.json`
2. Test REST endpoints
3. For WebSocket testing, use the Socket.io plugin for Postman

## 🔧 Integration Tips / نصائح التكامل

### React Integration

```javascript
import { useEffect, useState } from "react";
import { ChatClient } from "./ChatClient";

function useChatService(token, userId, userName, userType, governorate) {
  const [client, setClient] = useState(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    const chatClient = new ChatClient(
      token,
      userId,
      userName,
      userType,
      governorate,
    );

    chatClient.connect().then(() => {
      setConnected(true);
      setClient(chatClient);
    });

    // Listen for messages
    chatClient.socket.on("receive_message", (message) => {
      setMessages((prev) => [...prev, message]);
    });

    return () => chatClient.disconnect();
  }, [token, userId]);

  return { client, connected, messages };
}
```

### Vue.js Integration

```javascript
import { ref, onMounted, onUnmounted } from "vue";
import { ChatClient } from "./ChatClient";

export function useChatService(token, userId, userName, userType, governorate) {
  const client = ref(null);
  const connected = ref(false);
  const messages = ref([]);

  onMounted(async () => {
    client.value = new ChatClient(
      token,
      userId,
      userName,
      userType,
      governorate,
    );

    await client.value.connect();
    connected.value = true;

    client.value.socket.on("receive_message", (message) => {
      messages.value.push(message);
    });
  });

  onUnmounted(() => {
    if (client.value) {
      client.value.disconnect();
    }
  });

  return { client, connected, messages };
}
```

### Angular Integration

```typescript
import { Injectable, OnDestroy } from "@angular/core";
import { BehaviorSubject, Observable } from "rxjs";
import { ChatClient } from "./ChatClient";

@Injectable({ providedIn: "root" })
export class ChatService implements OnDestroy {
  private client: ChatClient;
  private messagesSubject = new BehaviorSubject<any[]>([]);
  public messages$: Observable<any[]> = this.messagesSubject.asObservable();

  async connect(
    token: string,
    userId: string,
    userName: string,
    userType: string,
    governorate: string,
  ) {
    this.client = new ChatClient(
      token,
      userId,
      userName,
      userType,
      governorate,
    );
    await this.client.connect();

    this.client.socket.on("receive_message", (message) => {
      const current = this.messagesSubject.value;
      this.messagesSubject.next([...current, message]);
    });
  }

  ngOnDestroy() {
    if (this.client) {
      this.client.disconnect();
    }
  }
}
```

## 📚 Additional Resources / مصادر إضافية

- [Socket.io Client Documentation](https://socket.io/docs/v4/client-api/)
- [Sahool API Documentation](http://localhost:8097/api-docs)
- [OpenAPI Specification](http://localhost:8097/api-docs.json)

## 🐛 Troubleshooting / حل المشاكل

### Connection Refused / رفض الاتصال

Make sure the chat service is running:

```bash
cd ..
npm start
```

### Authentication Failed / فشل المصادقة

Verify your JWT token is valid:

- Check expiration time
- Verify signature
- Ensure it includes `sub` and `role` fields

### Messages Not Received / عدم استقبال الرسائل

Check that:

- You've joined a room before sending messages
- The room ID is correct
- Event listeners are set up properly

## 📞 Support / الدعم

For issues or questions:

- Check the main API documentation
- Review error messages in console
- Contact: support@sahool.io

---

**Happy coding! 🚀**
**برمجة سعيدة! 🚀**
