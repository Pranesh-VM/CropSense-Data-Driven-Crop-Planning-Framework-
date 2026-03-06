import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/welcome');
  };

  return (
    <header className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
        {/* Logo */}
        <Link to="/dashboard" className="flex items-center space-x-2">
          <div className="text-2xl font-bold text-emerald-600">🌱 CropSense</div>
        </Link>

        {/* User Menu */}
        {user && (
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-gray-100 transition"
            >
              <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center text-white font-bold">
                {user.username?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="text-gray-700">{user.username}</span>
              <svg
                className={`w-4 h-4 transition transform ${isDropdownOpen ? 'rotate-180' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-2 border border-gray-200">
                <Link
                  to="/profile"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition"
                  onClick={() => setIsDropdownOpen(false)}
                >
                  Profile
                </Link>
                <hr className="my-1" />
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 transition"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
};
