import React, {useEffect, useState} from 'react';
import './App.css';
import {StartStopButton} from "./Components/StartStopButton";
import {PageTitle} from "./Components/PageTitle";
import {TextForm} from "./Components/TextForm";
import {DropdownForm} from "./Components/DropdownForm";
import {OffloadButton} from "./OffloadButton";
import {Field} from "./Components/Field";
import {AddrToggle} from "./Components/AddrToggle";

function App() {

    async function updateFields() {
        // const fetchResponse = await fetch(webserverURL + '/fields', {
        //     method: 'GET',
        //     headers: {
        //         Accept: 'application/json',
        //         'Content-Type': 'application/json'
        //     }
        // })
        // const json = await fetchResponse.json()
        const json = '[{"name":"driver","displayName":"Driver","type":"string","required":true,"dropdown":false,"automatic":false},{"name":"testingGoal","displayName":"Testing Goal","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"eventType","displayName":"Event Type","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"notes","displayName":"Notes","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"startTime","displayName":"Start Time/Date","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"endTime","displayName":"End Time/Date","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"location","displayName":"Location","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"conditions","displayName":"Conditions (ie dry, night time)","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"temperature","displayName":"Temperature (C)","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"aeroType","displayName":"Aero Type","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"MCUversion","displayName":"MCU Version","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"errors","displayName":"Errors","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"yawPIDValues","displayName":"Yaw Pid Values","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"TCSPIDValues","displayName":"TCS PID Values","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"TCSEnable","displayName":"TCS Enabled","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"yawPIDENable","displayName":"yaw PID Enabled","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"launchEnable","displayName":"Launch Enabled","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"normForceEnable","displayName":"Norm Force Enabled","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"mechPowerLimEnable","displayName":"Mech Power Lim. Enabled","type":"string","required":false,"dropdown":false,"automatic":false},{"name":"pidPowerLimEnable","displayName":"pid Power Lim. Enabled","type":"string","required":false,"dropdown":false,"automatic":false}]'
        setFields(JSON.parse(json))
        setData(new Array(fields.length).fill(undefined))

        return JSON.parse(json)
    }

    const [serverAddr, setServerAddr] = useState("http://192.168.203.1:6969")


    const [fields, setFields] = useState([])
    const [data, setData] = useState([]);
    const [recording, setRecording] = useState(false)

    useEffect(() => {
        updateFields().then(fields => setFields(fields))
    }, [])

    return (
        <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
            <AddrToggle serverAddr={serverAddr} setServerAddr={setServerAddr}/>
            <div className={"flex"}>
                <PageTitle/>
            </div>

            <div className={"flex flex-col gap-4 items-center justify-center"}>
                {fields.map((_field, index) => <Field fields={fields} data={data} setData={setData} index={index} recording={recording}/>)}
                {/*<StartStopButton recording={recording} setRecording={setRecording} driverInput={driverInput} trackNameInput={trackNameInput} eventTypeInput={eventTypeInput} drivetrainTypeInput={drivetrainTypeInput} massInput={massInput} wheelbaseInput={wheelbaseInput} firmwareRevInput={firmwareRevInput}/>*/}
            </div>

            <StartStopButton fields={fields} data={data} recording={recording} setRecording={setRecording}/>
            <OffloadButton/>
        </div>
    );
}

export default App;
