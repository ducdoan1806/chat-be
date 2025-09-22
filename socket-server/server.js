const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);
const room = {}; // roomId -> [userId]
const userSockets = {}; // userId -> [socketId]
const socketUser = {}; // socketId -> userId

const io = new Server(server, {
  cors: {
    origin: "http://localhost:5173",
    methods: ["GET", "POST"],
  },
});

io.on("connection", (socket) => {
  console.log("✅ Client connected:", socket.id);

  // Client phải gửi userId khi join room
  socket.on("join_room", ({ roomId, userId }) => {
    socket.join(roomId);

    // Lưu ánh xạ userId <-> socketId
    socketUser[socket.id] = userId;
    if (!userSockets[userId]) userSockets[userId] = [];
    if (!userSockets[userId].includes(socket.id)) {
      userSockets[userId].push(socket.id);
    }

    // Lưu userId vào room
    if (!room[roomId]) room[roomId] = [];
    if (!room[roomId].includes(userId)) {
      room[roomId].push(userId);
    }

    // Gửi danh sách userId trong phòng
    io.to(roomId).emit("room_members", room[roomId]);
    console.log(`✅ User ${userId} (${socket.id}) joined room: ${roomId}`);
  });

  socket.on("leave_room", ({ roomId, userId }) => {
    socket.leave(roomId);
    // Không xóa userId khỏi room, chỉ rời phòng thực tế
    io.to(roomId).emit("room_members", room[roomId]);
    console.log(`❌ User ${userId} (${socket.id}) left room: ${roomId}`);
  });

  socket.on("message", (msg) => {
    // msg.recipients là mảng userId, msg.conversation là roomId
    console.log(`📩 Message from ${socket.id}:`, msg);
    if (msg?.recipients && Array.isArray(msg.recipients)) {
      msg.recipients.forEach((userId) => {
        (userSockets[userId] || []).forEach((socketId) => {
          io.to(socketId).emit("message", msg);
        });
      });
    }
    socket.emit("message", `Server received: ${msg.body || msg}`);
  });

  socket.on("kick_user", ({ roomId, userId }) => {
    if (room[roomId]) {
      room[roomId] = room[roomId].filter((id) => id !== userId);
      io.to(roomId).emit("room_members", room[roomId]);
      // Thông báo cho tất cả socket của user bị kick
      (userSockets[userId] || []).forEach((socketId) => {
        io.to(socketId).emit("kicked", { roomId });
      });
      console.log(`🚫 Kicked user ${userId} from room ${roomId}`);
    }
  });

  socket.on("disconnect", () => {
    const userId = socketUser[socket.id];
    if (userId && userSockets[userId]) {
      userSockets[userId] = userSockets[userId].filter(
        (id) => id !== socket.id
      );
      if (userSockets[userId].length === 0) delete userSockets[userId];
    }
    delete socketUser[socket.id];
    console.log("❌ Client disconnected:", socket.id);
  });
});

server.listen(5000, () => {
  console.log("🚀 Socket.IO server running on http://localhost:5000");
});
