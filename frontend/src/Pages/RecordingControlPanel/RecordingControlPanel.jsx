import React, {useState, useEffect} from 'react';
import {StartStopButton} from "./StartStopButton";
import {Header} from "../Header/Header";
import {RecordingsList} from "./RecordingsList";
import {ErrorsList} from "./ErrorsList";
import {SectionTitle} from "./SectionTitle";
import {NetworkingUtils} from "../../Util/NetworkingUtils";
import {getDefaultData} from "../../Util/DataUtil";
import {Field} from "./Field";

export function RecordingControlPanel({recordingState, setRecordingState, useLocalhost, metadata, setMetadata}) {

    const recordingsFiller = [{status: "started", filename: "file1.mcap"},
                                                       {status: "stopped", filename: "file1.mcap"}]
    const errorsFiller = ["Error 1", "Error 2"]
    const metadataFiller = [{"displayName":"Driver","name":"driver","options":[],"type":"string"},{"displayName":"Notes","name":"notes","options":[],"type":"string"},{"displayName":"Errors","name":"errors","options":[],"type":"string"}]

    async function update() {
        NetworkingUtils.getRequest(NetworkingUtils.getURL(['recordings'], useLocalhost), recordingsFiller).then(response => {
            if (Array.isArray(response) && response.length === 4) {
                setRecordingState({
                    currFile: response[0],
                    recording: response[1],
                    recordings: response[2],
                    errors: response[3]
                });
            }
        })
        if (metadata.needUpdate) {
            NetworkingUtils.getRequest(NetworkingUtils.getURL(['fields'], useLocalhost), metadataFiller).then(response => {
                setMetadata({
                    needUpdate: false,
                    fields: response,
                    data: getDefaultData(response)
                })
            })
        }
    }

    useEffect(() => {
        let newMetadata = metadata
        newMetadata.needUpdate = true
        setMetadata(newMetadata)
        update().then()
    }, [useLocalhost])

    return (
        <div className={"flex flex-col gap-4 items-center justify-center"}>

            {metadata.fields.map((field, index) => <Field key={index} metadata={metadata} setMetadata={setMetadata} index={index}/>)}

            <StartStopButton recordingState={recordingState} setRecordingState={setRecordingState} useLocalhost={useLocalhost} update={update} metadata={metadata}/>

            <SectionTitle title={"Current Recording File"}/>

            <p>{recordingState.currFile == null ? "N/A" : recordingState.currFile}</p>

            <RecordingsList recordings={recordingState.recordings}/>

            <ErrorsList errors={recordingState.errors}/>

        </div>
    )

}