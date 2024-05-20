import React, {useEffect, useState} from 'react';
import {getDefaultData} from "../Util/DataUtil";
import {getURL} from "../Util/ServerAddrUtil";
import {EditModeToggle} from "../Components/EditModeToggle";
import {AddrToggle} from "./Header/AddrToggle";
import {PageTitle} from "./Header/PageTitle";
import {Field} from "../Components/Field";
import {StartStopButton} from "./RecordingControlPanel/StartStopButton";
import {OffloadButton} from "../Components/OffloadButton";
import {Header} from "./Header/Header";

export function MCAPRecorder({}) {

    const [useLocalhost, setUseLocalhost] = useState(false)
    const [fields, setFields] = useState([])
    const [data, setData] = useState([])
    const [recording, setRecording] = useState(false)

    useEffect(() => {
        updateFields().then(fields => {
            setFields(fields)
            setData(getDefaultData(fields))
        })
    }, [useLocalhost])

    async function updateFields() {
        let json;

        try {
            const fetchResponse = await fetch(getURL('fields', useLocalhost), {
                signal: AbortSignal.timeout(3000),
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            json = await fetchResponse.text()
        } catch (e) {
            //alert("WARNING: Using hardcoded fields");
            json = '[{"name":"driver","displayName":"Driver","type":"string","automatic":false,"options":["Shayan","Ryan"]},{"name":"testingGoal","displayName":"Testing Goal","type":"string","automatic":false,"options":[]}]'

        }
        return JSON.parse(json)
    }

    return (
        <>
            <main>
                <Header/>
                <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                    <AddrToggle useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>
                    <div className={"flex"}>
                        <PageTitle text={"MCAP Control Panel"}/>
                    </div>

                    <div className={"flex flex-col gap-4 items-center justify-center"}>
                        {fields.map((field, index) => <Field key={field.id} fields={fields} data={data}
                                                             setData={setData} index={index} recording={recording}
                                                             serverAddr={'http://192.168.203.1'}/>)}
                    </div>

                </div>
            </main>
            <footer className={"sticky bottom-0 bg-base-100"}>
                <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                    <StartStopButton fields={fields} data={data} recording={recording} setRecording={setRecording}
                                     serverAddr={'http://192.168.203.1'} useLocalhost={useLocalhost}/>
                    <OffloadButton/>
                </div>
            </footer>

        </>
    )
}