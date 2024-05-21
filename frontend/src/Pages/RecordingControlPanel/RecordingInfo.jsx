import React from 'react';

export function RecordingInfo({recordings, idx}) {
    return (
        <div className={"alert join-item -mt-2 -mb-1 border-base-content"}>
            <div className={"flex flex-row w-96"}>
                <p>{recordings[idx].filename}</p>
                <div className={"grow w-max"}/>
                <p>{recordings[idx].status}</p>
            </div>
        </div>
    )
}