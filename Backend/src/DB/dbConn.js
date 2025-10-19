import mongoose from "mongoose";

const dbConn = async () => {
  try {
    const connInstance = await mongoose.connect(process.env.DBCONN_URL);
    console.log(`Database connected successfully: ${connInstance.connection.host}`);
  } catch (error) {
    console.error("Database connection failed:", error);
    process.exit(1);
  }
};

export default dbConn;