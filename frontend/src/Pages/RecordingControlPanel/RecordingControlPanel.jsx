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

    function setCurrFile(file) {
        let newState = recordingState
        newState.currFile = file
        setRecordingState(newState)
    }

    function setRecording(recording) {
        let newState = recordingState
        newState.recording = recording
        setRecordingState(newState)
    }

    function setRecordings(recordings) {
        let newState = recordingState
        newState.recordings = recordings
        setRecordingState(newState)
    }

    function setErrors(errors) {
        let newState = recordingState
        newState.errors = errors
        setRecordingState(newState)
    }

    async function update() {
        NetworkingUtils.getRequest(NetworkingUtils.getURL(['writing_file'], useLocalhost), null).then(response => {
            setCurrFile(response)
        })
        NetworkingUtils.getRequest(NetworkingUtils.getURL(['recordings'], useLocalhost), recordingsFiller).then(response => {
            setRecordings(response)
        })
        NetworkingUtils.getRequest(NetworkingUtils.getURL(['errors'], useLocalhost), errorsFiller).then(response => {
            setErrors(response)
        })
    }

    useEffect(() => {
        update().then()
    }, [useLocalhost])

    return (
        <>
            <div className={"flex flex-col gap-4 items-center justify-center"}>
                <StartStopButton recording={recordingState.recording} setRecording={setRecording} useLocalhost={useLocalhost} update={update}/>

                <SectionTitle title={"Current Recording File"}/>

                <p>{recordingState.currFile == null ? "N/A" : recordingState.currFile}</p>

                <RecordingsList recordings={recordingState.recordings}/>

                <ErrorsList errors={recordingState.errors}/>

            </div>
        </>
    )

}