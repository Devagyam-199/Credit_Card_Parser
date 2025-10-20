import Statement from "../Models/statements.models.js";
import path from "path";
import fs from "fs";
import { spawn } from "child_process";
import APIError from "../Utils/apiError.utils.js";

const uploadStatement = async (req, res, next) => {
  try {
    if (!req.file) throw new APIError(400, "No file was uploaded");

    const uploadsDir = "./uploads";
    if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

    const tempFilePath = `${uploadsDir}/${Date.now()}-${req.file.originalname}`;
    fs.writeFileSync(tempFilePath, req.file.buffer);

    // Create initial entry (status: Pending)
    const newStatement = await Statement.create({
      fileName: req.file.originalname,
      status: "Pending",
    });

    const python = spawn("py", ["src/parser/main_parser.py", tempFilePath]);

    let parsedData = "";
    let pythonError = "";

    python.stdout.on("data", (data) => {
      parsedData += data.toString();
    });

    python.stderr.on("data", (data) => {
      pythonError += data.toString();
    });

    python.on("close", async (code) => {
      try {
        if (fs.existsSync(tempFilePath)) fs.unlinkSync(tempFilePath);

        if (code === 0 && parsedData.trim()) {
          // --- 🧠 CLEAN PARSED OUTPUT ---
          const cleanOutput = parsedData
            .trim()
            .replace(/^[^\{]*({[\s\S]*})[^\}]*$/m, "$1"); // Keep only valid JSON

          let jsonData;
          try {
            jsonData = JSON.parse(cleanOutput);
          } catch (parseErr) {
            console.error("JSON parse error:", parseErr, cleanOutput);
            newStatement.status = "Failed";
            newStatement.errorMessage = "Invalid JSON from parser.";
            await newStatement.save();
            return next(new APIError(500, "Failed to parse Python output."));
          }

          // --- 💾 SAVE TO MONGO ---
          newStatement.parsedData = jsonData;
          newStatement.issuerBank = jsonData.bank_detected || "Unknown";
          newStatement.status = "Parsed";
          await newStatement.save();

          return res.json({
            success: true,
            message: `File uploaded and parsed successfully (${newStatement.issuerBank})`,
            data: jsonData,
          });
        } else {
          console.error("Python error:", pythonError);
          newStatement.status = "Failed";
          newStatement.errorMessage = pythonError || `Python exited with code ${code}`;
          await newStatement.save();
          return next(new APIError(500, "Python parser failed."));
        }
      } catch (err) {
        console.error("Internal save error:", err);
        newStatement.status = "Failed";
        newStatement.errorMessage = err.message;
        await newStatement.save();
        return next(new APIError(500, "Server error after Python parse."));
      }
    });
  } catch (error) {
    next(error);
  }
};

export default uploadStatement;
