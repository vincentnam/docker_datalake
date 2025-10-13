import React from "react";
//
const Footer = () => {
  return (
    <footer className="fixed bottom-0 h-12 w-full  bg-amber-600 flex items-center justify-center rounded-md bg-clip-padding backdrop-filter backdrop-blur-lg bg-opacity-70 border border-gray-100 drop-shadow-lg animate-slideUp">
      <div className="container px-4 md:px-0 mx-auto flex justify-between items-center text-sm">
        <span>MIDOC - Espace de données {new Date().getFullYear()}</span>
        <div className="space-x-4">

          <a
            href="https://github.com/vincentnam/docker_datalake"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-red-100 transition-colors duration-300 hover:scale-110 inline-block"
          >
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;