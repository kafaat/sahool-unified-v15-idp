/**
 * Sahool Community Chat Service
 * خدمة الدردشة الحية لمجتمع سهول
 *
 * Real-time communication between farmers and agricultural experts
 * Port: 8097
 */

const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const cors = require("cors");
const { v4: uuidv4 } = require("uuid");
const jwt = require("jsonwebtoken");
const { setupSwagger } = require("./swagger");
const { PrismaClient } = require("@prisma/client");

// Initialize Prisma Client
const prisma = new PrismaClient({
  log: process.env.NODE_ENV === "development" ? ["query", "error", "warn"] : ["error"],
});

// Configuration
const PORT = process.env.PORT || 8097;
const SERVICE_NAME = "community-chat";
const SERVICE_VERSION = "1.0.0";

// JWT Configuration - SECURITY: JWT_SECRET_KEY is required
// ═══════════════════════════════════════════════════════════════════════════════
// SECURITY HARDENING: JWT_SECRET_KEY must always be configured
// المصادقة إلزامية دائماً - لا يمكن تشغيل الخدمة بدون JWT_SECRET_KEY
// ═══════════════════════════════════════════════════════════════════════════════
const JWT_SECRET_KEY = process.env.JWT_SECRET_KEY;

// SECURITY FIX: Hardcoded whitelist of allowed algorithms to prevent algorithm confusion attacks
// Never trust algorithm from environment variables or token header
const ALLOWED_ALGORITHMS = [
  "HS256",
  "HS384",
  "HS512",
  "RS256",
  "RS384",
  "RS512",
];

if (!JWT_SECRET_KEY || JWT_SECRET_KEY.trim().length === 0) {
  console.error("❌ FATAL: JWT_SECRET_KEY environment variable is required");
  console.error("❌ خطأ فادح: متغير JWT_SECRET_KEY مطلوب");
  console.error(
    "Set JWT_SECRET_KEY in your environment before starting the service",
  );
  process.exit(1);
}

// Authentication is always required - no bypass option
// المصادقة إلزامية دائماً - لا يمكن تعطيلها
const REQUIRE_AUTH = true;

// CORS Origins - configurable via environment
const ALLOWED_ORIGINS = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(",")
  : [
      "https://sahool.io",
      "https://admin.sahool.io",
      "https://app.sahool.io",
      "http://localhost:3000",
      "http://localhost:3001",
    ];

const app = express();
app.use(
  cors({
    origin: ALLOWED_ORIGINS,
    credentials: true,
  }),
);
app.use(express.json());

// Setup Swagger API Documentation
setupSwagger(app);

const server = http.createServer(app);

// JWT Verification middleware for Socket.io
// ═══════════════════════════════════════════════════════════════════════════════
// SECURITY HARDENING: Strict token verification - no fallbacks or anonymous access
// التحقق الصارم من التوكن - لا استثناءات ولا وصول مجهول
// ═══════════════════════════════════════════════════════════════════════════════
const verifyToken = (token) => {
  // SECURITY: Token is required - no exceptions
  if (!token || typeof token !== "string" || token.trim().length === 0) {
    throw new Error("Authentication token is required");
  }

  // SECURITY: JWT_SECRET_KEY is guaranteed to exist (checked at startup)
  // Verify token signature and expiration
  try {
    // SECURITY FIX: Decode header to validate algorithm before verification
    const decodedHeader = jwt.decode(token, { complete: true });
    if (!decodedHeader || !decodedHeader.header || !decodedHeader.header.alg) {
      throw new Error("Invalid token: missing algorithm");
    }

    // Reject 'none' algorithm explicitly
    if (decodedHeader.header.alg.toLowerCase() === "none") {
      throw new Error("Invalid token: none algorithm not allowed");
    }

    // Verify algorithm is in whitelist
    if (!ALLOWED_ALGORITHMS.includes(decodedHeader.header.alg)) {
      throw new Error(
        `Invalid token: unsupported algorithm ${decodedHeader.header.alg}`,
      );
    }

    // SECURITY FIX: Use hardcoded whitelist instead of environment variable
    const decoded = jwt.verify(token, JWT_SECRET_KEY, {
      algorithms: ALLOWED_ALGORITHMS,
    });

    // SECURITY: Additional validation of decoded token
    if (!decoded.sub) {
      throw new Error("Invalid token: missing subject (sub)");
    }

    return decoded;
  } catch (error) {
    // Provide specific error messages for debugging while maintaining security
    if (error.name === "TokenExpiredError") {
      throw new Error("Authentication token has expired");
    } else if (error.name === "JsonWebTokenError") {
      throw new Error("Invalid authentication token");
    } else if (error.name === "NotBeforeError") {
      throw new Error("Token not yet valid");
    }
    throw error;
  }
};

// Socket.io setup with CORS and authentication
const io = new Server(server, {
  cors: {
    origin: ALLOWED_ORIGINS,
    methods: ["GET", "POST"],
    credentials: true,
  },
  pingTimeout: 60000,
  pingInterval: 25000,
});

// Socket.io authentication middleware
// ═══════════════════════════════════════════════════════════════════════════════
// SECURITY HARDENING: Authentication is always required - no bypass mechanism
// المصادقة إلزامية دائماً - لا يوجد آلية لتجاوزها
// ═══════════════════════════════════════════════════════════════════════════════
io.use((socket, next) => {
  // SECURITY: Authentication is mandatory - removed REQUIRE_AUTH bypass
  // Extract token from auth or query (for backward compatibility)
  const token = socket.handshake.auth.token || socket.handshake.query.token;

  if (!token) {
    console.warn(
      "⚠️ Connection attempt without token from:",
      socket.handshake.address,
    );
    return next(new Error("Authentication required - no token provided"));
  }

  try {
    const decoded = verifyToken(token);

    // SECURITY: Additional user validation
    if (!decoded.sub || !decoded.role) {
      console.warn(
        "⚠️ Invalid token structure from:",
        socket.handshake.address,
      );
      return next(new Error("Invalid token structure"));
    }

    // Attach authenticated user to socket
    socket.user = decoded;

    console.log(`✅ Authenticated user: ${decoded.sub} (${decoded.role})`);
    next();
  } catch (err) {
    console.warn(
      "⚠️ Authentication failed:",
      err.message,
      "from:",
      socket.handshake.address,
    );
    return next(new Error("Authentication failed: " + err.message));
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// In-Memory Storage for ephemeral WebSocket state
// التخزين المؤقت في الذاكرة للحالة المؤقتة فقط
// Persistent data (rooms, messages) stored in PostgreSQL
// البيانات الدائمة (الغرف والرسائل) مخزنة في PostgreSQL
// ═══════════════════════════════════════════════════════════════════════════════

// Active users tracking (ephemeral - WebSocket connections)
const activeUsers = new Map();

// Online experts (ephemeral - WebSocket connections)
const onlineExperts = new Set();

// Maximum messages per room (for pagination)
const MAX_MESSAGES_PER_ROOM = 500;

// Default tenant ID for rooms (can be overridden)
const DEFAULT_TENANT_ID = process.env.DEFAULT_TENANT_ID || "sahool";

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════════

function getFormattedTime() {
  return new Date().toISOString();
}

// Database helper: Add message to room
async function addMessageToRoom(roomId, message) {
  try {
    // Ensure room exists
    let room = await prisma.chatRoom.findUnique({ where: { id: roomId } });
    if (!room) {
      // Create room if it doesn't exist
      room = await prisma.chatRoom.create({
        data: {
          id: roomId,
          name: roomId,
          tenantId: DEFAULT_TENANT_ID,
          type: roomId.startsWith("support_") ? "support" : "public",
        },
      });
    }

    // Create message
    const createdMessage = await prisma.message.create({
      data: {
        id: message.id,
        content: message.message,
        senderId: message.authorId || message.author,
        senderName: message.author,
        senderType: message.authorType,
        roomId: roomId,
        attachments: message.attachments || [],
        status: message.status || "delivered",
      },
    });

    return createdMessage;
  } catch (error) {
    console.error("❌ Error saving message to database:", error.message);
    // Return the message object even if DB save fails (for WebSocket delivery)
    return message;
  }
}

// Database helper: Get room messages
async function getRoomMessages(roomId, limit = MAX_MESSAGES_PER_ROOM) {
  try {
    const messages = await prisma.message.findMany({
      where: { roomId },
      orderBy: { createdAt: "asc" },
      take: limit,
    });

    // Transform to match existing message format
    return messages.map((msg) => ({
      id: msg.id,
      roomId: msg.roomId,
      author: msg.senderName,
      authorType: msg.senderType,
      message: msg.content,
      attachments: msg.attachments || [],
      timestamp: msg.createdAt.toISOString(),
      status: msg.status,
    }));
  } catch (error) {
    console.error("❌ Error fetching messages from database:", error.message);
    return [];
  }
}

// Database helper: Get or create room
async function getOrCreateRoom(roomId, roomData = {}) {
  try {
    let room = await prisma.chatRoom.findUnique({ where: { id: roomId } });

    if (!room) {
      room = await prisma.chatRoom.create({
        data: {
          id: roomId,
          name: roomData.name || roomId,
          tenantId: roomData.tenantId || DEFAULT_TENANT_ID,
          type: roomData.type || (roomId.startsWith("support_") ? "support" : "public"),
          status: roomData.status || "active",
          farmerId: roomData.farmerId,
          farmerName: roomData.farmerName,
          expertId: roomData.expertId,
          expertName: roomData.expertName,
          governorate: roomData.governorate,
          topic: roomData.topic,
          diagnosisId: roomData.diagnosisId,
          createdBy: roomData.createdBy,
        },
      });
    }

    return room;
  } catch (error) {
    console.error("❌ Error getting/creating room:", error.message);
    return null;
  }
}

// Database helper: Update room
async function updateRoom(roomId, updateData) {
  try {
    const room = await prisma.chatRoom.update({
      where: { id: roomId },
      data: updateData,
    });
    return room;
  } catch (error) {
    console.error("❌ Error updating room:", error.message);
    return null;
  }
}

// Database helper: Get room by ID
async function getRoom(roomId) {
  try {
    const room = await prisma.chatRoom.findUnique({ where: { id: roomId } });
    return room;
  } catch (error) {
    console.error("❌ Error fetching room:", error.message);
    return null;
  }
}

// Database helper: Add member to room
async function addMemberToRoom(roomId, memberData) {
  try {
    const member = await prisma.chatMember.upsert({
      where: {
        userId_roomId: {
          userId: memberData.odolUserId || memberData.name,
          roomId: roomId,
        },
      },
      update: {
        userName: memberData.name,
        userType: memberData.type,
      },
      create: {
        userId: memberData.odolUserId || memberData.name,
        odolUserId: memberData.odolUserId,
        userName: memberData.name,
        userType: memberData.type,
        roomId: roomId,
        role: "member",
      },
    });
    return member;
  } catch (error) {
    console.error("❌ Error adding member to room:", error.message);
    return null;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Socket.io Event Handlers
// ═══════════════════════════════════════════════════════════════════════════════

io.on("connection", (socket) => {
  console.log(`🔌 User connected: ${socket.id}`);

  // ─────────────────────────────────────────────────────────────────────────────
  // User Registration
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("register_user", (data) => {
    const { userId, userName, userType, governorate } = data;

    activeUsers.set(socket.id, {
      id: socket.id,
      odolUserId: userId,
      name: userName,
      nameAr: data.userNameAr || userName,
      type: userType, // 'farmer' or 'expert'
      governorate: governorate,
      connectedAt: getFormattedTime(),
    });

    if (userType === "expert") {
      onlineExperts.add(socket.id);
      // Notify all connected clients about new expert
      io.emit("expert_online", { expertId: userId, expertName: userName });
    }

    console.log(`👤 User registered: ${userName} (${userType})`);

    // Send confirmation
    socket.emit("registration_confirmed", {
      success: true,
      socketId: socket.id,
      onlineExperts: onlineExperts.size,
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Join Room (Chat Session)
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("join_room", async (data) => {
    const { roomId, userName, userType } = data;

    // ═══════════════════════════════════════════════════════════════════════════
    // SECURITY: Room Access Validation
    // التحقق من صلاحية الوصول للغرفة
    // ═══════════════════════════════════════════════════════════════════════════

    // Validate room ID format (prevent injection)
    if (!roomId || typeof roomId !== "string" || roomId.length > 100) {
      socket.emit("error", {
        code: "INVALID_ROOM_ID",
        message: "معرف الغرفة غير صالح",
      });
      return;
    }

    // Validate userName
    if (!userName || typeof userName !== "string" || userName.length > 100) {
      socket.emit("error", {
        code: "INVALID_USERNAME",
        message: "اسم المستخدم غير صالح",
      });
      return;
    }

    // Validate userType
    const validUserTypes = ["farmer", "expert", "admin", "support"];
    if (!validUserTypes.includes(userType)) {
      socket.emit("error", {
        code: "INVALID_USER_TYPE",
        message: "نوع المستخدم غير صالح",
      });
      return;
    }

    // Check if user is authenticated (from middleware)
    const authenticatedUser = socket.user;

    // For support rooms, verify access rights
    if (roomId.startsWith("support_")) {
      const room = await getRoom(roomId);
      if (room) {
        // Only the original farmer or assigned expert can join support rooms
        const isOriginalFarmer = room.farmerId === authenticatedUser?.sub;
        const isAssignedExpert = room.expertId === authenticatedUser?.sub;
        const isAdmin =
          authenticatedUser?.role === "admin" ||
          authenticatedUser?.role === "super_admin";

        if (
          !isOriginalFarmer &&
          !isAssignedExpert &&
          !isAdmin &&
          userType !== "expert"
        ) {
          socket.emit("error", {
            code: "ACCESS_DENIED",
            message: "لا يمكنك الوصول لهذه الغرفة",
          });
          console.warn(
            `⚠️ Access denied to room ${roomId} for user ${userName}`,
          );
          return;
        }
      }
    }

    // ═══════════════════════════════════════════════════════════════════════════

    socket.join(roomId);
    console.log(`🚪 ${userName} joined room: ${roomId}`);

    // Get or create room in database
    const room = await getOrCreateRoom(roomId, {
      createdBy: authenticatedUser?.sub || userName,
    });

    // Add participant to room
    if (room) {
      await addMemberToRoom(roomId, {
        name: userName,
        type: userType,
        odolUserId: authenticatedUser?.sub,
      });
    }

    // Send message history to joining user
    const history = await getRoomMessages(roomId);
    socket.emit("load_history", history);

    // Notify room about new participant
    socket.to(roomId).emit("user_joined", {
      userName,
      userType,
      time: getFormattedTime(),
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Send Message
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("send_message", async (data) => {
    const { roomId, author, authorType, message, attachments } = data;

    // ═══════════════════════════════════════════════════════════════════════════
    // SECURITY: Message Validation
    // التحقق من صحة الرسالة
    // ═══════════════════════════════════════════════════════════════════════════

    // Validate roomId
    if (!roomId || typeof roomId !== "string" || roomId.length > 100) {
      socket.emit("error", {
        code: "INVALID_ROOM_ID",
        message: "معرف الغرفة غير صالح",
      });
      return;
    }

    // Validate author
    if (!author || typeof author !== "string" || author.length > 100) {
      socket.emit("error", {
        code: "INVALID_AUTHOR",
        message: "اسم المؤلف غير صالح",
      });
      return;
    }

    // Validate message content
    if (!message || typeof message !== "string") {
      socket.emit("error", {
        code: "INVALID_MESSAGE",
        message: "محتوى الرسالة غير صالح",
      });
      return;
    }

    // Limit message length (prevent DoS)
    const MAX_MESSAGE_LENGTH = 10000;
    if (message.length > MAX_MESSAGE_LENGTH) {
      socket.emit("error", {
        code: "MESSAGE_TOO_LONG",
        message: `الرسالة طويلة جداً`,
      });
      return;
    }

    // Validate authorType
    const validAuthorTypes = ["farmer", "expert", "admin", "support", "system"];
    const safeAuthorType = validAuthorTypes.includes(authorType)
      ? authorType
      : "farmer";

    // Validate attachments (if provided)
    let safeAttachments = [];
    if (attachments && Array.isArray(attachments)) {
      const ALLOWED_DOMAINS = ["sahool.io", "sahool.app", "localhost"];
      safeAttachments = attachments.slice(0, 10).filter((att) => {
        if (!att || typeof att !== "object") return false;
        if (att.url && typeof att.url === "string") {
          try {
            const url = new URL(att.url);
            return ALLOWED_DOMAINS.some((d) => url.hostname.endsWith(d));
          } catch {
            return false;
          }
        }
        return true;
      });
    }

    // Sanitize message content (basic XSS prevention)
    const sanitizedMessage = message
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#x27;");

    // ═══════════════════════════════════════════════════════════════════════════

    const messageData = {
      id: uuidv4(),
      roomId,
      author,
      authorId: socket.user?.sub,
      authorType: safeAuthorType,
      message: sanitizedMessage,
      attachments: safeAttachments,
      timestamp: getFormattedTime(),
      status: "delivered",
    };

    // Store message in database
    await addMessageToRoom(roomId, messageData);

    // Broadcast to all users in room (including sender for confirmation)
    io.to(roomId).emit("receive_message", messageData);

    console.log(`💬 Message in ${roomId}: "${message.substring(0, 50)}..."`);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Typing Indicator
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("typing_start", (data) => {
    socket.to(data.roomId).emit("user_typing", {
      userName: data.userName,
      isTyping: true,
    });
  });

  socket.on("typing_stop", (data) => {
    socket.to(data.roomId).emit("user_typing", {
      userName: data.userName,
      isTyping: false,
    });
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Request Expert Help (Farmer initiates)
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("request_expert", async (data) => {
    const { farmerId, farmerName, governorate, topic, diagnosisId } = data;

    // Create a new support room
    const roomId = `support_${farmerId}_${Date.now()}`;

    const supportRequest = {
      roomId,
      farmerId,
      farmerName,
      governorate,
      topic: topic || "استشارة زراعية",
      diagnosisId, // Link to disease diagnosis if any
      status: "pending",
      createdAt: getFormattedTime(),
    };

    // Store room in database
    await getOrCreateRoom(roomId, {
      name: topic || "استشارة زراعية",
      type: "support",
      farmerId,
      farmerName,
      governorate,
      topic: topic || "استشارة زراعية",
      diagnosisId,
      status: "pending",
      createdBy: socket.user?.sub || farmerId,
    });

    // Join farmer to the room
    socket.join(roomId);

    // Notify all online experts about new request
    io.emit("new_support_request", supportRequest);

    // Confirm to farmer
    socket.emit("expert_request_created", {
      success: true,
      roomId,
      message: "تم إرسال طلبك. سيتواصل معك خبير قريباً.",
    });

    console.log(`🆘 Expert request from ${farmerName}: ${topic}`);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Expert Accepts Request
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("accept_request", async (data) => {
    const { roomId, expertId, expertName } = data;

    const room = await getRoom(roomId);
    if (room) {
      // Update room in database
      await updateRoom(roomId, {
        expertId,
        expertName,
        status: "active",
        acceptedAt: new Date(),
      });

      // Expert joins the room
      socket.join(roomId);

      // Notify farmer that expert has joined
      io.to(roomId).emit("expert_joined", {
        expertId,
        expertName,
        message: `${expertName} انضم للمحادثة`,
      });

      // Notify other experts that this request is taken
      io.emit("request_taken", { roomId, expertName });

      console.log(`✅ Expert ${expertName} accepted request ${roomId}`);
    }
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Leave Room
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("leave_room", (data) => {
    const { roomId, userName } = data;
    socket.leave(roomId);
    socket.to(roomId).emit("user_left", { userName, time: getFormattedTime() });
    console.log(`👋 ${userName} left room: ${roomId}`);
  });

  // ─────────────────────────────────────────────────────────────────────────────
  // Disconnect
  // ─────────────────────────────────────────────────────────────────────────────

  socket.on("disconnect", () => {
    const user = activeUsers.get(socket.id);

    if (user) {
      console.log(`🔌 User disconnected: ${user.name}`);

      if (user.type === "expert") {
        onlineExperts.delete(socket.id);
        io.emit("expert_offline", { expertId: user.userId });
      }

      activeUsers.delete(socket.id);
    } else {
      console.log(`🔌 Unknown user disconnected: ${socket.id}`);
    }
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
// REST API Endpoints
// ═══════════════════════════════════════════════════════════════════════════════

// Health check
app.get("/healthz", async (req, res) => {
  let dbHealthy = false;
  try {
    await prisma.$queryRaw`SELECT 1`;
    dbHealthy = true;
  } catch (error) {
    console.error("❌ Database health check failed:", error.message);
  }

  res.json({
    status: dbHealthy ? "healthy" : "degraded",
    service: SERVICE_NAME,
    version: SERVICE_VERSION,
    database: dbHealthy ? "connected" : "disconnected",
    activeConnections: io.engine.clientsCount,
    onlineExperts: onlineExperts.size,
    timestamp: getFormattedTime(),
  });
});

// Readiness check
app.get("/readyz", async (req, res) => {
  let dbReady = false;
  try {
    await prisma.$queryRaw`SELECT 1`;
    dbReady = true;
  } catch (error) {
    console.error("❌ Database readiness check failed:", error.message);
  }

  if (!dbReady) {
    return res.status(503).json({
      status: "not_ready",
      database: "disconnected",
    });
  }

  res.json({
    status: "ready",
    database: "connected",
  });
});

// Get active support requests (for Admin Dashboard)
app.get("/v1/requests", async (req, res) => {
  try {
    const { status } = req.query;

    const whereClause = {
      type: "support",
    };

    if (status) {
      whereClause.status = status;
    }

    const rooms = await prisma.chatRoom.findMany({
      where: whereClause,
      orderBy: { createdAt: "desc" },
      include: {
        _count: {
          select: { messages: true },
        },
      },
    });

    // Transform to match existing API format
    const requests = rooms.map((room) => ({
      roomId: room.id,
      farmerId: room.farmerId,
      farmerName: room.farmerName,
      expertId: room.expertId,
      expertName: room.expertName,
      governorate: room.governorate,
      topic: room.topic,
      diagnosisId: room.diagnosisId,
      status: room.status,
      createdAt: room.createdAt.toISOString(),
      acceptedAt: room.acceptedAt?.toISOString(),
      messageCount: room._count.messages,
    }));

    res.json(requests);
  } catch (error) {
    console.error("❌ Error fetching requests:", error.message);
    res.status(500).json({ error: "Failed to fetch requests" });
  }
});

// Get room history
app.get("/v1/rooms/:roomId/messages", async (req, res) => {
  try {
    const { roomId } = req.params;
    const { limit = 500, offset = 0 } = req.query;

    const messages = await prisma.message.findMany({
      where: { roomId },
      orderBy: { createdAt: "asc" },
      take: parseInt(limit),
      skip: parseInt(offset),
    });

    // Transform to match existing format
    const formattedMessages = messages.map((msg) => ({
      id: msg.id,
      roomId: msg.roomId,
      author: msg.senderName,
      authorType: msg.senderType,
      message: msg.content,
      attachments: msg.attachments || [],
      timestamp: msg.createdAt.toISOString(),
      status: msg.status,
    }));

    res.json(formattedMessages);
  } catch (error) {
    console.error("❌ Error fetching messages:", error.message);
    res.status(500).json({ error: "Failed to fetch messages" });
  }
});

// Get online experts count
app.get("/v1/experts/online", (req, res) => {
  res.json({
    count: onlineExperts.size,
    available: onlineExperts.size > 0,
  });
});

// Get stats
app.get("/v1/stats", async (req, res) => {
  try {
    const totalMessages = await prisma.message.count();
    const totalRooms = await prisma.chatRoom.count();
    const activeRooms = await prisma.chatRoom.count({
      where: { status: "active" },
    });

    res.json({
      totalConnections: activeUsers.size,
      onlineExperts: onlineExperts.size,
      activeRooms,
      totalRooms,
      totalMessages,
      timestamp: getFormattedTime(),
    });
  } catch (error) {
    console.error("❌ Error fetching stats:", error.message);
    res.status(500).json({
      totalConnections: activeUsers.size,
      onlineExperts: onlineExperts.size,
      activeRooms: 0,
      totalMessages: 0,
      timestamp: getFormattedTime(),
      error: "Failed to fetch database stats",
    });
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// Graceful Shutdown
// ═══════════════════════════════════════════════════════════════════════════════

async function gracefulShutdown(signal) {
  console.log(`\n📴 Received ${signal}. Shutting down gracefully...`);

  // Close all WebSocket connections
  io.close();

  // Disconnect from database
  await prisma.$disconnect();

  console.log("👋 Goodbye!");
  process.exit(0);
}

process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("SIGINT", () => gracefulShutdown("SIGINT"));

// ═══════════════════════════════════════════════════════════════════════════════
// Start Server
// ═══════════════════════════════════════════════════════════════════════════════

async function startServer() {
  try {
    // Test database connection
    await prisma.$connect();
    console.log("✅ Database connected successfully");

    server.listen(PORT, () => {
      console.log(`
╔═══════════════════════════════════════════════════════════════╗
║         🌿 Sahool Community Chat Service 🌿                   ║
║                                                               ║
║   Service: ${SERVICE_NAME.padEnd(20)} Version: ${SERVICE_VERSION}        ║
║   Port: ${PORT}                                                ║
║   Database: PostgreSQL (Prisma)                               ║
║                                                               ║
║   خدمة الدردشة الحية لمجتمع سهول الزراعي                     ║
╚═══════════════════════════════════════════════════════════════╝
      `);
    });
  } catch (error) {
    console.error("❌ Failed to start server:", error.message);
    process.exit(1);
  }
}

startServer();
