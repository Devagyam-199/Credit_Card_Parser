import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import Header from './components/Header.jsx';
import UploadPage from './pages/UploadPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';

function App() {
  const [parsedData, setParsedData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleNewUpload = () => {
    setParsedData(null); // Reset parsedData when navigating to upload
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <Routes>
          <Route 
            path="/" 
            element={
              parsedData ? <Navigate to="/dashboard" /> : <UploadPage setParsedData={setParsedData} setLoading={setLoading} loading={loading} />
            } 
          />
          <Route 
            path="/dashboard" 
            element={parsedData ? <DashboardPage parsedData={parsedData} onNewUpload={handleNewUpload} /> : <Navigate to="/" />} 
          />
          <Route path="/upload" element={<UploadPage setParsedData={setParsedData} setLoading={setLoading} loading={loading} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;