import React from 'react';

export function RecordingInfo({recordings, idx}) {
    return (
        <div className={"alert join-item"}>
            <div className={"flex flex-row w-96"}>
                <p>Filename.mcap</p>
                <div className={"grow w-max"}/>
                <p>Started</p>
            </div>
        </div>
    )
}