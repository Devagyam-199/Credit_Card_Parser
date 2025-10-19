import mongoose from "mongoose";

const statementSchema = new mongoose.Schema({
    fileName : {
        type: String,
        required: true,
    },
    issuerBank:{
        type: String,
        required: false,
        default: "Unknown",
    },
    uploadDate:{
        type: Date,
        default: Date.now,
    },
    parsedData:{
        type: Object,
        default:{},
    },
    status:{
        type:String,
        enum:["Pending","Parsed","Failed"],
        default:"Pending",
    },
    errorMessage:{
        type:String,
        default:"Something went wrong...",
    }
},{timestamps: true})

const Statement = mongoose.model("Statement",statementSchema);

export default Statement;