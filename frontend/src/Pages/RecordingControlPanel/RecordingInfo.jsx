import React from 'react';

export function RecordingInfo({recordings, idx}) {
    return (
        <div className={"alert join-item -mt-2 -mb-1 border-base-content"}>
            <div className={"flex flex-row w-96"}>
                <p>Filename.mcap</p>
                <div className={"grow w-max"}/>
                <p>Started</p>
            </div>
        </div>
    )
}