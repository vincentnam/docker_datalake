import React from "react";
import { useDrop } from "react-dnd";
import { ItemTypes } from "../../constants/itemTypes";
import { moveObject } from "../../utils/fileUtils";
import { useNavigate } from "react-router-dom";

const FolderRow = ({ node, bucketName }) => {
  const navigate = useNavigate();
  const [{ isOver }, drop] = useDrop(() => ({
    accept: ItemTypes.FILE,
    drop: (item) => moveObject(bucketName, item.key, node.key),
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }));

  return (
    <span
      ref={drop}
      className={`cursor-pointer ${isOver ? "bg-gray-200" : ""}`}
      onClick={(e) => {
        e.stopPropagation();
        navigate(`/buckets/${bucketName}?path=${node.key}`);
      }}
    >
      {node.data.name}
    </span>
  );
};

export default FolderRow;