import { Link } from "react-router-dom";
import { CreditCard, TrendingUp, Menu, X } from "lucide-react";
import { useState } from "react";

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-200/50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4 sm:py-6">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-4 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-full blur-lg opacity-30 group-hover:opacity-50 transition-opacity duration-500"></div>
              <div className="relative bg-gradient-to-r from-indigo-600 to-purple-600 p-2.5 rounded-full transform group-hover:scale-110 transition-transform duration-300">
                <CreditCard className="w-7 h-7 text-white" />
              </div>
            </div>
            <span className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent animate-pulse-slow">
              StatementAI
            </span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link 
              to="/dashboard" 
              className="text-gray-700 hover:text-indigo-600 font-semibold transition-colors duration-300 flex items-center space-x-2 group hover:bg-indigo-50 px-3 py-2 rounded-lg"
            >
              <TrendingUp className="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span>Dashboard</span>
            </Link>
          </nav>

          {/* Mobile Menu Button */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-full hover:bg-gray-100 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <X className="w-7 h-7 text-gray-800" />
            ) : (
              <Menu className="w-7 h-7 text-gray-800" />
            )}
          </button>
        </div>
      </div>
      
      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white/95 backdrop-blur-sm animate-slideDown">
          <div className="px-4 py-4 space-y-2">
            <Link 
              to="/dashboard" 
              className="flex items-center space-x-3 px-4 py-3 rounded-xl hover:bg-indigo-50 transition-all duration-300 group"
              onClick={() => setMobileMenuOpen(false)}
            >
              <TrendingUp className="w-5 h-5 text-indigo-600" />
              <span className="text-gray-800 group-hover:text-indigo-600 font-semibold">Dashboard</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};

export default Header;