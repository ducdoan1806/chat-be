const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

const app = express();
const server = http.createServer(app);

// Khởi tạo Socket.IO server
const io = new Server(server, {
  cors: {
    origin: "http://localhost:5173",
    methods: ["GET", "POST"],
  },
});

io.on("connection", (socket) => {
  console.log("✅ Client connected:", socket.id);

  socket.on("message", (msg) => {
    console.log(`📩 Message from ${socket.id}:`, msg);
    socket.emit("message", `Server received: ${msg}`);
  });

  socket.on("disconnect", () => {
    console.log("❌ Client disconnected:", socket.id);
  });
});

// Chạy server
server.listen(5000, () => {
  console.log("🚀 Socket.IO server running on http://localhost:5000");
});
