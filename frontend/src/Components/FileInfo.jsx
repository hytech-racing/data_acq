import React from 'react';

export function FileInfo({offloaded, fileData, index, useLocalhost}) {

    function edit() {
        alert("This feature has not been implemented yet")
    }
    
    function offloadFile() {
        alert("This feature has not been implemented yet")
    }
    
    return (
        <div className={"bg-base-300 p-6 rounded-lg"}>
            <article className={"article"}>
                <p>{fileData[index].name}</p>
            </article>
            <div className={"flex flex-row gap-10 w-80 bg-base-300 pt-4"}>
                <div className={"grow w-max"}/>
                <button className={"btn " + (offloaded ? "btn-error" : "btn-success")} onClick={edit}>
                    {offloaded ? "Delete From Car" : "Offload to Server"}
                </button>
            </div>
        </div>
    )

}