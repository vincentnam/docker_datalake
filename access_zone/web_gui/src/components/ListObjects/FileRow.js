import React from "react";
import { useDrag } from "react-dnd";
import { ItemTypes } from "../../constants/itemTypes";

const FileRow = ({ node, setSelectedNode, setSidebarVisible }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.FILE,
    item: { key: node.key },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  return (
    <span
      ref={drag}
      className={`cursor-pointer text-blue-500 hover:text-blue-700 transition-colors duration-200 ${isDragging ? "opacity-50" : ""}`}
      onClick={(e) => {
        e.stopPropagation();
        setSelectedNode(node);
        setSidebarVisible(true);
      }}
    >
      {node.data.name}
    </span>
  );
};

export default FileRow;