# CrediWiz: Credit Card Statement Parser

[![Node.js](https://img.shields.io/badge/Node.js-v18+-green.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-v18-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CrediWiz is a web application designed to parse credit card statements in PDF format, providing users with detailed financial insights through an interactive dashboard. Built with a MERN stack (MongoDB, Express.js, React, Node.js) and enhanced with Python for PDF processing, it supports statements from major Indian banks like Axis, HDFC, ICICI, and IDFC, categorizing transactions into spending categories such as Fuel, Food, Shopping, Travel, Bills, and Entertainment.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [File Structure](#file-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Features

- **PDF Upload and Parsing**: Upload credit card statements and extract details like cardholder name, card number, due dates, totals, and transactions.
- **Bank Detection**: Automatically identifies the issuing bank using pattern-based detection.
- **Transaction Categorization**: Categorization of spending into intuitive categories.
- **Interactive Dashboard**: Visualize spending with pie charts, filterable transaction tables, and AI-generated insights.
- **Responsive Design**: Mobile-friendly UI with drag-and-drop upload and smooth navigation.
- **Error Handling**: Robust backend and frontend error management.

## Tech Stack

### Backend
- **Node.js & Express**: API server and routing.
- **Python**: PDF parsing with `pdfplumber` and custom bank parsers.
- **MongoDB & Mongoose**: Data persistence.
- **Multer**: File upload handling.
- **Child Process**: Python script execution.

### Frontend
- **React**: Core framework with React Router.
- **Axios**: API requests.
- **Recharts**: Data visualization.
- **Tailwind CSS**: Styling.
- **Lucide React**: Icons.

### Tools
- **Netlify**: Frontend hosting.
- **Render**: Backend hosting.

## File Structure
Credit_Card_Parser/
├── Backend/
│   └── src/
│       ├── Controllers/
│       │   └── upload.controllers.js
│       ├── DB/
│       │   └── dbConn.js
│       ├── Models/
│       │   └── statements.models.js
│       ├── Routes/
│       │   └── upload.routes.js
│       ├── Utils/
│       │   └── apiError.utils.js
│       ├── parser/
│       │   ├── banks/
│       │   │   ├── axis_parser.py
│       │   │   ├── general_parser.py
│       │   │   ├── hdfc_parser.py
│       │   │   ├── icici_parser.py
│       │   │   └── idfc_parser.py
│       │   ├── bank_detect.py
│       │   └── main_parser.py
│       ├── app.js
│       ├── index.js
│       ├── package-lock.json
│       ├── package.json
│       └── requirements.txt
│
├── Frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       │   ├── AIInsights.jsx
│       │   ├── Header.jsx
│       │   ├── SpendingInsights.jsx
│       │   └── TransactionTable.jsx
│       ├── pages/
│       │   ├── DashboardPage.jsx
│       │   └── UploadPage.jsx
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── eslint.config.js
│       ├── vite.config.js
│       ├── package-lock.json
│       └── package.json
│
├── real_bank_statements_for_testing/
│   ├── axis_sample.pdf
│   ├── hdfc_sample.pdf
│   └── idfc_sample.pdf
│
└── README.md

## Installation

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- MongoDB (local or Atlas)
- Git

### Backend Setup
1. Navigate to the backend directory:
2. Install dependencies:
3. Set up environment variables in a `.env` file:
4. Install Python dependencies:
5. Start the server:


### Frontend Setup
1. Navigate to the frontend directory:
2. Install dependencies:
3. Start the development server:


## Usage
1. **Upload a Statement**:
- Visit `https://crediwiz.netlify.app`
- Drag-and-drop or select a PDF from `real_bank_statements_for_testing`.
- Click "Upload & Parse".
2. **View Dashboard**:
- After parsing, navigate to `/dashboard` to see insights and transactions.
3. **New Upload**:
- Click "New Upload" to reset and parse another statement.

## Deployment
- **Backend**: Deploy on Render (`https://credit-card-parser-backend-u1mf.onrender.com`).
- **Frontend**: Deploy on Netlify (`https://crediwiz.netlify.app`).
- Update `UploadPage.jsx` with the backend URL for API calls.

## Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
- Built with open-source tools like `pdfplumber` and `Recharts`.
- Inspired by the need for financial insight tools.
- Special thanks to the community for support and contributions.

*Last updated: 02:39 PM IST, Thursday, October 23, 2025*