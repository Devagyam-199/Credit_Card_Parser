import { useState } from 'react';
import axios from 'axios';

const UploadPage = ({ setParsedData, setLoading, loading }) => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('https://credit-card-parser-backend-u1mf.onrender.com/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setParsedData(response.data.data);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-6 px-2 sm:px-4 lg:px-8 bg-gradient-to-br from-gray-100 to-gray-200">
      <div className="max-w-md w-full space-y-6 sm:space-y-8 bg-white rounded-xl shadow-2xl p-6 sm:p-8 transform transition-all duration-300 hover:shadow-3xl">
        <div>
          <h2 className="text-center text-3xl sm:text-4xl font-extrabold text-gray-900 bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text">
            Upload Your Statement
          </h2>
          <p className="mt-2 text-center text-sm sm:text-base text-gray-600">
            Drag and drop or choose a PDF file to parse.
          </p>
        </div>
        <form onSubmit={handleSubmit} onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop} className="space-y-6">
          <div className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-xl bg-gray-50 p-6 transition-all duration-300 hover:border-indigo-500 hover:bg-gray-100">
            <div className={dragActive ? "hidden" : "text-center space-y-4 animate-fadeIn"}>
              <svg className="mx-auto h-12 w-12 sm:h-16 sm:w-16 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                <path d="M28 8H12a4 4 0 00-4 4v24a4 4 0 004 4h24a4 4 0 004-4V20l-12-12zM36 32h-8a2 2 0 01-2-2v-8a2 2 0 012-2h8v12zm-12-14V10l10 10h-10a2 2 0 01-2-2z" />
              </svg>
              <p className="text-sm sm:text-base text-gray-500">Drag your PDF here or</p>
              <label className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                <span className="px-4 py-2 inline-flex items-center">Choose File</span>
                <input
                  type="file"
                  className="sr-only"
                  accept=".pdf"
                  onChange={handleChange}
                  aria-label="Upload PDF file"
                />
              </label>
            </div>
            {dragActive && (
              <div className="text-center space-y-4 animate-pulse">
                <svg className="mx-auto h-12 w-12 sm:h-16 sm:w-16 text-indigo-500" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                  <path d="M2 6a2 2 0 012-2h12a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zm10 0a2 2 0 11-4 0 2 2 0 014 0zm-2 6a2 2 0 100-4 2 2 0 000 4z" />
                </svg>
                <p className="text-sm sm:text-base text-indigo-600">Drop your PDF here</p>
              </div>
            )}
            {file && (
              <p className="text-xs sm:text-sm text-gray-500 mt-4 bg-gray-100 px-3 py-1 rounded-full animate-slideUp">{file.name}</p>
            )}
          </div>
          <button
            type="submit"
            disabled={!file || loading}
            className="group relative w-full flex justify-center py-3 px-6 border border-transparent text-base font-medium rounded-xl text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transform transition-all duration-300 hover:scale-105"
          >
            {loading ? (
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : null}
            {loading ? 'Parsing...' : 'Upload & Parse'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UploadPage;