import React from "react"

export const isImage = (contentType, fileNameWithExtension) =>{
    return contentType.includes("image") || fileNameWithExtension.includes("image")
}


export const getFileIcon = (obj) =>{
    const {
        name:fileName
    } =obj

    const extension = fileName.substr(fileName.lastIndexOf('.') + 1);
    return <span className={`fiv-viv fiv-icon-${extension}`}></span>
}