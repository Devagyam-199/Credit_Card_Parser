import Statement from "../Models/statements.models.js";
import path from "path";
import fs from "fs";
import { spawn } from "child_process";
import APIError from "../Utils/apiError.utils.js";

const uploadStatement = async (req, res, next) => {
  try {
    if (!req.file) {
      throw new APIError(400, "No file was uploaded");
    }

    const newStatement = await Statement.create({
      fileName: req.file.originalname,
      status: "Pending",
    });

    const tempFilePath = `./uploads/${Date.now()}-${req.file.originalname}`;
    await import("fs").then((fs) =>
      fs.promises.writeFile(tempFilePath, req.file.buffer)
    );

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
      await fs.promises.unlink(tempFilePath);

      if (code === 0) {
        try {
          const jsonData = JSON.parse(parsedData);
          newStatement.parsedData = jsonData;
          newStatement.status = "Parsed";
          await newStatement.save();

          res.json({
            success: true,
            message: "File uploaded and parsed successfully",
            data: jsonData,
          });
        } catch (error) {
          newStatement.status = "Failed";
          newStatement.errorMessage = "Parsing JSON failed";
          await newStatement.save();
          next(new APIError(500, "Failed to parse the statement data"));
        }
      } else {
        console.error("Python error:", pythonError);
        newStatement.status = "Failed";
        newStatement.errorMessage =
          pythonError || `Python exited with code ${code}`;
        await newStatement.save();
        next(new APIError(500, "Python parser failed"));
      }
    });
  } catch (error) {
    next(error);
  }
};

export default uploadStatement;
