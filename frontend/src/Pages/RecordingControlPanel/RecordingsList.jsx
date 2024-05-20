import React from 'react';
import {RecordingInfo} from "./RecordingInfo";
import {SectionTitle} from "./SectionTitle";

export function RecordingsList({recordings}) {

    function getRecordingRows() {
        let recordingRows = []
        for (let i = recordings.length - 1; i >= 0; i--) {
            recordingRows.push(<RecordingInfo key={i} recordings={recordings} idx={i}/>)
        }
        return recordingRows
    }

    return (
        <>
            <SectionTitle title={"Recordings"}/>
            <div className="join join-vertical">
                {getRecordingRows()}
            </div>
        </>
    )
}