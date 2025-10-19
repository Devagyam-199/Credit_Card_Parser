import uploadStatement from "../Controllers/upload.controllers.js";
import express from "express";
import multer from "multer";

const router = express.Router();

const storage = multer.memoryStorage();
const upload = multer({ storage });

router.post("/upload", upload.single("file"), uploadStatement);

export default router;