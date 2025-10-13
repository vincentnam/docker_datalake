const AppBody = ({ children }) => {
  return (
    <div className="container mx-auto bg-white/30 backdrop-blur-md rounded-lg shadow-lg p-6 animate-fadeIn">
      {children}
    </div>
  );
};

export default AppBody;