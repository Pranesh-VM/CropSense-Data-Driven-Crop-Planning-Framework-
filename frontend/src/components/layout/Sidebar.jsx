import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: '📊 Dashboard', icon: '📊' },
    { path: '/quick-recommendation', label: '⚡ Quick Recommend', icon: '⚡' },
    { path: '/cycle/new', label: '🌾 New Cycle', icon: '🌾' },
    { path: '/cycle/active', label: '⏱️ Active Cycle', icon: '⏱️' },
    { path: '/cycle/history', label: '📈 History', icon: '📈' },
    { path: '/profile', label: '👤 Profile', icon: '👤' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Mobile Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed bottom-4 right-4 z-40 bg-emerald-500 text-white p-3 rounded-full shadow-lg"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed md:static left-0 top-16 h-screen w-64 bg-white border-r border-gray-200 transition-transform duration-300 z-30 ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <nav className="p-4 space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className={`block px-4 py-3 rounded-lg transition ${
                isActive(item.path)
                  ? 'bg-emerald-50 text-emerald-600 font-semibold border-l-4 border-emerald-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="mr-2">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-20 top-16"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};
