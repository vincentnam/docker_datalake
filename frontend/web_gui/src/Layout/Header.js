import React, { useState } from "react";
import { Link } from "react-router-dom";

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const [theme, setTheme] = useState("light");

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);
  // const toggleTheme = () => {
  //   const newTheme = theme === "light" ? "dark" : "light";
  //   setTheme(newTheme);
  //   document.documentElement.setAttribute("data-theme", newTheme);
  // };

  return (
    <header className="w-full h-16 bg-amber-600 rounded-md bg-clip-padding backdrop-filter backdrop-blur-lg bg-opacity-70 border  border-gray-100 drop-shadow-lg sticky top-0 z-50">
      <div className="container px-4 md:px-0 h-full mx-auto flex justify-between items-center">
        <Link to="/" className="flex items-center space-x-2 group">
          <span className="text-xl font-bold hover:scale-110 group-hover:text-red-100 transition-colors duration-300">
            Lac de données
          </span>
        </Link>

        {/* Bouton hamburger */}
        <button
          className="md:hidden focus:outline-none neon-button"
          onClick={toggleMenu}
          aria-label="Toggle menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d={isMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"}
            />
          </svg>
        </button>

        {/* Menu */}
        <nav
            className={`${
                isMenuOpen ? "flex" : "hidden"
            } md:flex flex-col md:flex-row absolute md:static top-16 left-0 w-full md:w-auto bg-pink-700/90 md:bg-transparent p-4 md:p-0 space-y-4 md:space-y-0 md:space-x-6 animate-slideInRight glass-effect`}
        >
          <Link
              to="/buckets"
              className="opacity-70 hover:scale-110 hover:text-red-100 hover:opacity-100 transition-all duration-300"
              onClick={() => setIsMenuOpen(false)}
          >
            Vos données (Buckets)
          </Link>
          {/*<button*/}
          {/*    onClick={toggleTheme}*/}
          {/*    className="hover:text-purple-600 transition-all duration-300"*/}
          {/*>*/}
          {/*  {theme === "light" ? "Mode sombre" : "Mode clair"}*/}
          {/*</button>*/}
        </nav>
      </div>
    </header>
  );
};

export default Header;