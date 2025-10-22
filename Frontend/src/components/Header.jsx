import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-2 sm:py-4">
          <div className="flex items-center">
            <Link to="/" className="text-xl sm:text-2xl font-bold text-gray-900">
              Credit Statement Parser
            </Link>
          </div>
          <nav className="space-x-2 sm:space-x-4">
            <Link to="/dashboard" className="text-gray-500 hover:text-gray-700 text-sm sm:text-base">Dashboard</Link>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;