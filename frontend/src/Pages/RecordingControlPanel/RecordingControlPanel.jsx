import React, {useState, useEffect} from 'react';
import {StartStopButton} from "./StartStopButton";
import {Header} from "../Header/Header";
import {RecordingsList} from "./RecordingsList";
import {ErrorsList} from "./ErrorsList";
import {SectionTitle} from "./SectionTitle";
import {NetworkingUtils} from "../../Util/NetworkingUtils";
import {getDefaultData} from "../../Util/DataUtil";
import {Field} from "./Field";

export function RecordingControlPanel({recordingState, setRecordingState, useLocalhost, fields, setFields, data, setData}) {

    const recordingsFiller = [{status: "started", filename: "file1.mcap"},
                                                       {status: "stopped", filename: "file1.mcap"}]
    const errorsFiller = ["Error 1", "Error 2"]
    const metadataFiller = [{"name":"driver","displayName":"Driver","type":"string","automatic":false,"options":["Shayan","Ryan"]},{"name":"testingGoal","displayName":"Testing Goal","type":"string","automatic":false,"options":[]}]

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
        if (fields.length == 0){ //only run when page loads
            NetworkingUtils.getRequest(NetworkingUtils.getURL(['fields'], useLocalhost), metadataFiller).then(response => {
                setFields(response)
                setData(getDefaultData(response));
            })  
        }
        
    }

    useEffect(() => {
        update().then()
        // or run when toggle is switched
        NetworkingUtils.getRequest(NetworkingUtils.getURL(['fields'], useLocalhost), metadataFiller).then(response => {
            setFields(response)
            setData(getDefaultData(response));
        })  
    }, [useLocalhost])

    return (
        <div className={"flex flex-col gap-4 items-center justify-center"}>
            <div className={"flex flex-col gap-4 items-center justify-center"}>
                        {fields.map((field, index) => <Field key={field.id} fields={fields} data={data}
                                                             setData={setData} index={index} recording={recordingState.recording}
                                                             serverAddr={'http://192.168.203.1'}/>)}
            </div>
            <StartStopButton recordingState={recordingState} setRecordingState={setRecordingState} useLocalhost={useLocalhost} update={update} fields={fields} data={data}/>

            <SectionTitle title={"Current Recording File"}/>

            <p>{recordingState.currFile == null ? "N/A" : recordingState.currFile}</p>

            <RecordingsList recordings={recordingState.recordings}/>

            <ErrorsList errors={recordingState.errors}/>

        </div>
    )

}