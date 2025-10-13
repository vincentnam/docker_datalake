import React, { Fragment } from "react";
import Header from "./Header";
import AppBody from "./AppBody";
import Footer from "./Footer";

const AppLayout = ({ children }) => {
  return (
    <Fragment>
      <Header />
      <div className="flex flex-col min-h-screen bg-gradient-to-br from-gray-100 to-gray-200">
        <main className="flex-grow p-5 transition-all duration-300 ease-in-out">
          <AppBody>{children}</AppBody>
        </main>
      </div>
      <Footer />
    </Fragment>
  );
};

export default AppLayout;