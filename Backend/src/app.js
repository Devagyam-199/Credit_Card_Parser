import express from 'express';
import cors from "cors";
import multer from "multer";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import globalErrorHandler from './Utils/errorHandler.utils.js';

const app = express();

const corsOptions = {
  origin: "http://localhost:5173",
  methods: ["GET", "POST", "PUT", "DELETE"],
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: true,
};
app.use(cors(corsOptions));
app.use(express.json());
app.use(globalErrorHandler);

import router from "./Routes/upload.routes.js";
app.use("/api",router);

export default app;