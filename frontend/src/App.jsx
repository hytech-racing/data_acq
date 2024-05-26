import React, {useEffect, useState} from 'react';
import './App.css';
import {EditSSOT} from "./Pages/EditSSOT";
import {Header} from "./Pages/Header/Header"
import {RecordingControlPanel} from "./Pages/RecordingControlPanel/RecordingControlPanel";
import {ParamsControlPanel} from "./Pages/ParamsControlPanel/ParamsControlPanel";

function App() {

    const [useLocalhost, setUseLocalhost] = useState(false)
    const [currPanel, setCurrPanel] = useState("Recording")

    const [recordingState, setRecordingState] = useState({currFile: null, recording: false, recordings: [], errors: []})
    const [params, setParams] = useState({})

    const [metadata, setMetadata] = useState({needUpdate: false, fields: [], data: []})

    function getPanel() {
        if (currPanel === "Recording"){
            return (
                <RecordingControlPanel recordingState={recordingState} setRecordingState={setRecordingState} useLocalhost={useLocalhost} metadata={metadata} setMetadata={setMetadata}/>
            )
        } else if (currPanel === "Edit SSOT"){
            return (
                <EditSSOT metadata={metadata} setMetadata={setMetadata} useLocalhost={useLocalhost}/>
            )
        } else if (currPanel === "Params") {
            return (
                <ParamsControlPanel params={params} setParams={setParams} useLocalhost={useLocalhost}/>
            )
        } else {
            return (
                <></>
            )
        }
    }

    return (
        <>
            <Header currPanel={currPanel} setCurrPanel={setCurrPanel} useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>
            {getPanel()}
        </>
    )
}


export default App;
