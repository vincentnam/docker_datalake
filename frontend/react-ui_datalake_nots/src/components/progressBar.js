import React, {useEffect, useRef, useState} from 'react';


export default function ProgressBar(props){
    return (
        <div className="ProgressBar">
            <div className="Progress"
            style={{ width: props.progress + '%'}}
            />
        </div>

    )


}
