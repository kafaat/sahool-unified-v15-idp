/**
 * Sahool Community Chat - Client Integration Example
 * مثال على التكامل مع خدمة الدردشة
 *
 * This file demonstrates how to integrate with the Community Chat Service
 * from a client application (web or mobile).
 */

const io = require("socket.io-client");

// ═══════════════════════════════════════════════════════════════════════════════
// Configuration / الإعدادات
// ═══════════════════════════════════════════════════════════════════════════════

const CHAT_SERVICE_URL =
  process.env.CHAT_SERVICE_URL || "http://localhost:8097";
const JWT_TOKEN = process.env.JWT_TOKEN || "your-jwt-token-here";

// ═══════════════════════════════════════════════════════════════════════════════
// Chat Client Class / فئة عميل الدردشة
// ═══════════════════════════════════════════════════════════════════════════════

class ChatClient {
  constructor(token, userId, userName, userType, governorate) {
    this.token = token;
    this.userId = userId;
    this.userName = userName;
    this.userType = userType;
    this.governorate = governorate;
    this.socket = null;
    this.currentRoom = null;
  }

  /**
   * Connect to chat service
   * الاتصال بخدمة الدردشة
   */
  connect() {
    return new Promise((resolve, reject) => {
      console.log("🔌 Connecting to chat service...");

      this.socket = io(CHAT_SERVICE_URL, {
        auth: { token: this.token },
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
      });

      // Connection successful
      this.socket.on("connect", () => {
        console.log("✅ Connected to chat service:", this.socket.id);
        this.registerUser();
      });

      // Registration confirmed
      this.socket.on("registration_confirmed", (data) => {
        console.log("✅ User registered successfully:", data);
        resolve(data);
      });

      // Connection error
      this.socket.on("connect_error", (error) => {
        console.error("❌ Connection error:", error.message);
        reject(error);
      });

      // Disconnected
      this.socket.on("disconnect", (reason) => {
        console.log("🔌 Disconnected:", reason);
      });

      // Error events
      this.socket.on("error", (error) => {
        console.error("❌ Error:", error);
      });

      // Setup all event listeners
      this.setupEventListeners();
    });
  }

  /**
   * Register user on connection
   * تسجيل المستخدم عند الاتصال
   */
  registerUser() {
    this.socket.emit("register_user", {
      userId: this.userId,
      userName: this.userName,
      userType: this.userType,
      governorate: this.governorate,
    });
  }

  /**
   * Join a chat room
   * الانضمام إلى غرفة دردشة
   */
  joinRoom(roomId) {
    return new Promise((resolve) => {
      console.log(`🚪 Joining room: ${roomId}`);

      this.currentRoom = roomId;

      this.socket.emit("join_room", {
        roomId,
        userName: this.userName,
        userType: this.userType,
      });

      // Wait for history to load
      this.socket.once("load_history", (messages) => {
        console.log(`📜 Loaded ${messages.length} messages`);
        resolve(messages);
      });
    });
  }

  /**
   * Leave current room
   * مغادرة الغرفة الحالية
   */
  leaveRoom() {
    if (!this.currentRoom) {
      console.warn("⚠️ No active room to leave");
      return;
    }

    this.socket.emit("leave_room", {
      roomId: this.currentRoom,
      userName: this.userName,
    });

    this.currentRoom = null;
  }

  /**
   * Send a message
   * إرسال رسالة
   */
  sendMessage(message, attachments = []) {
    if (!this.currentRoom) {
      console.error("❌ Cannot send message: Not in a room");
      return;
    }

    this.socket.emit("send_message", {
      roomId: this.currentRoom,
      author: this.userName,
      authorType: this.userType,
      message,
      attachments,
    });

    console.log(`💬 Sent message: "${message.substring(0, 50)}..."`);
  }

  /**
   * Start typing indicator
   * بدء مؤشر الكتابة
   */
  startTyping() {
    if (!this.currentRoom) return;

    this.socket.emit("typing_start", {
      roomId: this.currentRoom,
      userName: this.userName,
    });
  }

  /**
   * Stop typing indicator
   * إيقاف مؤشر الكتابة
   */
  stopTyping() {
    if (!this.currentRoom) return;

    this.socket.emit("typing_stop", {
      roomId: this.currentRoom,
      userName: this.userName,
    });
  }

  /**
   * Request expert help (Farmer only)
   * طلب مساعدة خبير (للمزارعين فقط)
   */
  requestExpert(topic, diagnosisId = null) {
    if (this.userType !== "farmer") {
      console.error("❌ Only farmers can request expert help");
      return;
    }

    return new Promise((resolve) => {
      this.socket.emit("request_expert", {
        farmerId: this.userId,
        farmerName: this.userName,
        governorate: this.governorate,
        topic,
        diagnosisId,
      });

      this.socket.once("expert_request_created", (data) => {
        console.log("✅ Expert request created:", data);
        resolve(data);
      });
    });
  }

  /**
   * Accept support request (Expert only)
   * قبول طلب الدعم (للخبراء فقط)
   */
  acceptRequest(roomId) {
    if (this.userType !== "expert") {
      console.error("❌ Only experts can accept requests");
      return;
    }

    this.socket.emit("accept_request", {
      roomId,
      expertId: this.userId,
      expertName: this.userName,
    });

    console.log(`✅ Accepted request: ${roomId}`);
  }

  /**
   * Setup event listeners
   * إعداد مستمعي الأحداث
   */
  setupEventListeners() {
    // Message received
    this.socket.on("receive_message", (message) => {
      console.log(
        "📩 New message from %s: %s",
        message.author,
        message.message,
      );
      // Handle new message (update UI, etc.)
    });

    // User joined room
    this.socket.on("user_joined", (data) => {
      console.log("👋 %s (%s) joined the room", data.userName, data.userType);
    });

    // User left room
    this.socket.on("user_left", (data) => {
      console.log("👋 %s left the room", data.userName);
    });

    // Typing indicator
    this.socket.on("user_typing", (data) => {
      if (data.isTyping) {
        console.log("✍️ %s is typing...", data.userName);
      } else {
        console.log("✍️ %s stopped typing", data.userName);
      }
    });

    // Expert online
    this.socket.on("expert_online", (data) => {
      console.log("🟢 Expert %s is now online", data.expertName);
    });

    // Expert offline
    this.socket.on("expert_offline", (data) => {
      console.log("🔴 Expert %s is now offline", data.expertId);
    });

    // New support request (for experts)
    this.socket.on("new_support_request", (request) => {
      console.log(
        "🆘 New support request from %s: %s",
        request.farmerName,
        request.topic,
      );
      // Notify expert about new request
    });

    // Expert joined (for farmers)
    this.socket.on("expert_joined", (data) => {
      console.log("✅ Expert %s joined your consultation", data.expertName);
    });

    // Request taken (for experts)
    this.socket.on("request_taken", (data) => {
      console.log(
        "ℹ️ Request %s was taken by %s",
        data.roomId,
        data.expertName,
      );
    });
  }

  /**
   * Disconnect from chat service
   * قطع الاتصال من خدمة الدردشة
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      console.log("👋 Disconnected from chat service");
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Example Usage - Farmer / مثال الاستخدام - مزارع
// ═══════════════════════════════════════════════════════════════════════════════

async function farmerExample() {
  console.log("\n═══════════════════════════════════════");
  console.log("Farmer Example / مثال المزارع");
  console.log("═══════════════════════════════════════\n");

  const farmer = new ChatClient(
    JWT_TOKEN,
    "farmer_12345",
    "محمد أحمد",
    "farmer",
    "القاهرة",
  );

  try {
    // Connect
    await farmer.connect();

    // Request expert help
    const request = await farmer.requestExpert(
      "مرض في نباتات الطماطم",
      "diag_98765",
    );

    // Join the support room
    const messages = await farmer.joinRoom(request.roomId);
    console.log("Initial messages:", messages);

    // Send a message
    farmer.sendMessage(
      "السلام عليكم، أحتاج مساعدة في تشخيص مرض في نباتات الطماطم",
    );

    // Start typing
    farmer.startTyping();
    setTimeout(() => farmer.stopTyping(), 2000);

    // Wait a bit before disconnecting
    setTimeout(() => {
      farmer.leaveRoom();
      farmer.disconnect();
    }, 10000);
  } catch (error) {
    console.error("Error:", error);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Example Usage - Expert / مثال الاستخدام - خبير
// ═══════════════════════════════════════════════════════════════════════════════

async function expertExample() {
  console.log("\n═══════════════════════════════════════");
  console.log("Expert Example / مثال الخبير");
  console.log("═══════════════════════════════════════\n");

  const expert = new ChatClient(
    JWT_TOKEN,
    "expert_123",
    "د. أحمد الخبير",
    "expert",
    "القاهرة",
  );

  try {
    // Connect
    await expert.connect();

    // Listen for new support requests
    expert.socket.on("new_support_request", async (request) => {
      console.log("New request received:", request);

      // Accept the request
      expert.acceptRequest(request.roomId);

      // Join the room
      await expert.joinRoom(request.roomId);

      // Send greeting
      expert.sendMessage("وعليكم السلام، أنا هنا لمساعدتك. ما هي المشكلة؟");
    });

    // Keep connection alive
    setTimeout(() => {
      expert.disconnect();
    }, 60000);
  } catch (error) {
    console.error("Error:", error);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// REST API Examples / أمثلة REST API
// ═══════════════════════════════════════════════════════════════════════════════

async function restApiExamples() {
  const baseUrl = CHAT_SERVICE_URL;

  console.log("\n═══════════════════════════════════════");
  console.log("REST API Examples / أمثلة REST API");
  console.log("═══════════════════════════════════════\n");

  // Health check
  try {
    const healthResponse = await fetch(`${baseUrl}/healthz`);
    const health = await healthResponse.json();
    console.log("Health:", health);
  } catch (error) {
    console.error("Health check error:", error);
  }

  // Get online experts
  try {
    const expertsResponse = await fetch(`${baseUrl}/v1/experts/online`);
    const experts = await expertsResponse.json();
    console.log("Online experts:", experts);
  } catch (error) {
    console.error("Get experts error:", error);
  }

  // Get support requests
  try {
    const requestsResponse = await fetch(
      `${baseUrl}/v1/requests?status=pending`,
    );
    const requests = await requestsResponse.json();
    console.log("Pending requests:", requests);
  } catch (error) {
    console.error("Get requests error:", error);
  }

  // Get room messages
  try {
    const roomId = "support_12345_1735295400000";
    const messagesResponse = await fetch(
      `${baseUrl}/v1/rooms/${roomId}/messages`,
    );
    const messages = await messagesResponse.json();
    console.log(`Messages in room ${roomId}:`, messages);
  } catch (error) {
    console.error("Get messages error:", error);
  }

  // Get statistics
  try {
    const statsResponse = await fetch(`${baseUrl}/v1/stats`);
    const stats = await statsResponse.json();
    console.log("Statistics:", stats);
  } catch (error) {
    console.error("Get stats error:", error);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Run Examples / تشغيل الأمثلة
// ═══════════════════════════════════════════════════════════════════════════════

if (require.main === module) {
  console.log("Choose example to run:");
  console.log("1. node client-example.js farmer");
  console.log("2. node client-example.js expert");
  console.log("3. node client-example.js rest");

  const mode = process.argv[2];

  switch (mode) {
    case "farmer":
      farmerExample();
      break;
    case "expert":
      expertExample();
      break;
    case "rest":
      restApiExamples();
      break;
    default:
      console.log("Please specify: farmer, expert, or rest");
      console.log("Example: node client-example.js farmer");
  }
}

module.exports = { ChatClient };
