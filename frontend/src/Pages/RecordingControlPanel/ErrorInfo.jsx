import React from 'react';

export function ErrorInfo({errors, idx}) {
    return (
        <div className={"alert join-item -mt-2 -mb-1 border-base-content"}>
            <div className={"flex flex-row w-96"}>
                <p>{errors[idx]}</p>
                <div className={"grow w-max"}/>
            </div>
        </div>
    )
}