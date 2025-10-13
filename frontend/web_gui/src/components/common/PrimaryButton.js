const PrimaryButton = ({ children, className = "", ...props }) => {
  return (
    <button
      className={`bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors duration-300 neon-button ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

export default PrimaryButton;