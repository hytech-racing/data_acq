import React, {useState, useEffect} from 'react';
import {StartStopButton} from "./StartStopButton";
import {Header} from "../Header/Header";
import {RecordingsList} from "./RecordingsList";
import {ErrorsList} from "./ErrorsList";
import {SectionTitle} from "./SectionTitle";
import {NetworkingUtils} from "../../Util/NetworkingUtils";

export function RecordingControlPanel({recordingState, setRecordingState, useLocalhost}) {

    const recordingsFiller = [{status: "started", filename: "file1.mcap"},
                                                       {status: "stopped", filename: "file1.mcap"}]
    const errorsFiller = ["Error 1", "Error 2"]

    async function update() {
        NetworkingUtils.getRequest(NetworkingUtils.getURL(['recordings'], useLocalhost), recordingsFiller).then(response => {
            if (Array.isArray(response) && response.length === 4) {
                setRecordingState({
                  currFile: response[0],
                  recording: response[1],
                  recordings: response[2],
                  errors: response[3]
                });
                console.log('State updated:', {
                    currFile: response[0],
                    recording: response[1],
                    recordings: response[2],
                    errors: response[3]})
            }
            
        })
        
    }

    useEffect(() => {
        update().then()
    }, [useLocalhost])

    return (
        <div className={"flex flex-col gap-4 items-center justify-center"}>
            <StartStopButton recordingState={recordingState} setRecordingState={setRecordingState} useLocalhost={useLocalhost} update={update}/>

            <SectionTitle title={"Current Recording File"}/>

            <p>{recordingState.currFile == null ? "N/A" : recordingState.currFile}</p>

            <RecordingsList recordings={recordingState.recordings}/>

            <ErrorsList errors={recordingState.errors}/>

        </div>
    )

}