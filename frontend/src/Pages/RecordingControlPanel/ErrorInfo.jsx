import React from 'react';

export function ErrorInfo({errors, idx}) {
    return (
        <div className={"alert join-item"}>
            <div className={"flex flex-row w-96"}>
                <p>Error message</p>
                <div className={"grow w-max"}/>
            </div>
        </div>
    )
}