import app from "./app.js";
import dotenv from "dotenv";
import dbConn from "./DB/dbConn.js";

dotenv.config();

const PORT = process.env.PORT || 8080;
dbConn().then(()=>{
    app.listen(PORT,()=>{
        console.log(`server is running on port ${PORT}`);
    })
})
.catch((err)=>{
    console.error("Failed to connect to the database:", err);
})