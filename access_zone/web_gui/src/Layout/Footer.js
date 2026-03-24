// src/Layout/Footer.js
import React from "react";
import { GitBranch } from "lucide-react";

const Footer = () => {
  return (
    <footer className="fixed bottom-0 left-0 right-0 h-14 z-40 bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700 border-t border-white/20 shadow-2xl">
      <div className="max-w-7xl mx-auto px-6 h-full flex items-center justify-between text-white/90 text-sm">
        {/* Left side */}
        <div className="flex items-center gap-2">
          <span className="font-medium">MIDOC</span>
          <span className="text-white/60">—</span>
          <span>Espace de données {new Date().getFullYear()}</span>
        </div>

        {/* Right side */}
        <a
          href="https://github.com/vincentnam/docker_datalake"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 hover:text-white transition-all duration-300 hover:scale-105 group"
        >
          <GitBranch
            size={18}
            className="group-hover:rotate-12 transition-transform"
          />
          <span className="font-medium">GitHub</span>
        </a>
      </div>
    </footer>
  );
};

export default Footer;
