import React, {useState, useEffect} from 'react';
import {StartStopButton} from "./StartStopButton";
import {Header} from "../Header/Header";
import {RecordingsList} from "./RecordingsList";
import {ErrorsList} from "./ErrorsList";
import {SectionTitle} from "./SectionTitle";
import {NetworkingUtils} from "../../Util/NetworkingUtils";

export function RecordingControlPanel({}) {

    const recordingsFiller = [{status: "started", filename: "file1.mcap"},
                                                        {status: "stopped", filename: "file1.mcap"}]
    const errorsFiller = ["Error 1", "Error 2"]

    const [useLocalhost, setUseLocalhost] = useState(false);
    const [currFile, setCurrFile] = useState(null);
    const [recording, setRecording] = useState(false);
    const [recordings, setRecordings] = useState([]);
    const [errors, setErrors] = useState({});

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
            <Header title={"Recording Control Panel"} useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>

            <div className={"flex flex-col gap-4 items-center justify-center"}>
                <StartStopButton recording={recording} setRecording={setRecording} useLocalhost={useLocalhost} update={update}/>

                <SectionTitle title={"Current Recording File"}/>

                <p>{currFile == null ? "N/A" : currFile}</p>

                <RecordingsList recordings={recordings}/>

                <ErrorsList errors={errors}/>

            </div>
        </>
    )

}