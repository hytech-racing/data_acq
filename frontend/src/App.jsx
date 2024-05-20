import React, {useEffect, useState} from 'react';
import './App.css';
import {MCAPRecorder} from "./Pages/MCAPRecorder";
import {EditSSOT} from "./Pages/EditSSOT";
import {Files} from "./Pages/Files"
import {Header} from "./Pages/Header/Header"
import {RecordingControlPanel} from "./Pages/RecordingControlPanel/RecordingControlPanel";

function App() {

    const [useLocalhost, setUseLocalhost] = useState(false)
    const [currPanel, setCurrPanel] = useState("Recording")

    const [recordingState, setRecordingState] = useState({currFile: null, recording: false, recordings: [], errors: []})
    const [ssot, setSsot] = useState('')

    function getPanel() {
        if (currPanel === "Recording"){
            return (
                <RecordingControlPanel recordingState={recordingState} setRecordingState={setRecordingState} useLocalhost={useLocalhost}/>
            )
        } else if (currPanel === "Edit SSOT"){
            return (
                <EditSSOT ssot={ssot} setSsot={setSsot} useLocalhost={useLocalhost}/>
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
