import React, {useState} from 'react';
import {StartStopButton} from "./StartStopButton";
import {Header} from "../Header/Header";
import {RecordingsList} from "./RecordingsList";
import {ErrorsList} from "./ErrorsList";
import {SectionTitle} from "./SectionTitle";

export function RecordingControlPanel({}) {

    const [useLocalhost, setUseLocalhost] = useState(false);
    const [currFile, setCurrFile] = useState(null);
    const [recording, setRecording] = useState(false);
    const [recordings, setRecordings] = useState([]);
    const [errors, setErrors] = useState({});

    async function update() {
        // TODO
    }

    return (
        <>
            <Header title={"Recording Control Panel"} useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>

            <div className={"flex flex-col gap-4 items-center justify-center"}>
                <StartStopButton recording={recording} setRecording={setRecording} useLocalhost={useLocalhost} update={update}/>

                <SectionTitle title={"Current Recording File"}/>

                <p>filename.mcap</p>

                <RecordingsList/>

                <ErrorsList/>

            </div>
        </>
    )

}