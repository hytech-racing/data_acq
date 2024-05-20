import React from 'react';
import {RecordingInfo} from "./RecordingInfo";
import {SectionTitle} from "./SectionTitle";

export function RecordingsList({recordings}) {
    return (
        <>
            <SectionTitle title={"Recordings"}/>
            <div className="join join-vertical">
                <RecordingInfo/>
                <RecordingInfo/>
                <RecordingInfo/>
                <RecordingInfo/>
                <RecordingInfo/>
            </div>
        </>
    )
}