import React, {useEffect, useState} from 'react';
import './App.css';
import {MCAPRecorder} from "./Pages/MCAPRecorder";
import {EditSSOT} from "./Pages/EditSSOT";
import {Files} from "./Pages/Files"
import {Header} from "./Pages/Header/Header"
import {RecordingControlPanel} from "./Pages/RecordingControlPanel/RecordingControlPanel";
import {ParamsControlPanel} from "./Pages/ParamsControlPanel/ParamsControlPanel";

function App() {

    const [useLocalhost, setUseLocalhost] = useState(false)
    const [currPanel, setCurrPanel] = useState("Recording")

    const [recordingState, setRecordingState] = useState({currFile: null, recording: false, recordings: [], errors: []})
    const [ssot, setSsot] = useState('')
    const [params, setParams] = useState({})

    const [fields, setFields] = useState([])
    const [data, setData] = useState([])

    function getPanel() {
        if (currPanel === "Recording"){
            return (
                <RecordingControlPanel recordingState={recordingState} setRecordingState={setRecordingState} useLocalhost={useLocalhost} fields={fields} setFields={setFields} data={data} setData={setData}/>
            )
        } else if (currPanel === "Edit SSOT"){
            return (
                <EditSSOT ssot={ssot} setSsot={setSsot} useLocalhost={useLocalhost}/>
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
