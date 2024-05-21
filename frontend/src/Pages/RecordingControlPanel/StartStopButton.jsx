import React from "react";
import { useState } from "react";
import {getURL} from "../../Util/ServerAddrUtil";
import {getFormattedDate} from "../../Util/DateUtil";
import {getMetadata} from "../../Util/DataUtil";
import {wait} from "@testing-library/user-event/dist/utils";

export function StartStopButton({recordingState, setRecordingState, useLocalhost, update}) {

    const [waitingForResponse, setWaitingForResponse] = useState(false);
    const [time, setTime] = useState("");

    function getButtonStyle() {
        return recordingState.recording ? "btn btn-error" : "btn btn-success"
    }

    function getButtonText() {
        if (waitingForResponse) {
            return "..."
        }
        return recordingState.recording ? "Stop Recording" : "Start Recording"
    }

    async function stopRecording() {
        if(waitingForResponse) {
            return false
        }

        setWaitingForResponse(true);

        let body = '{"startTime": ' + JSON.stringify(time) + "}"//getMetadata(fields, data, time)

        const fetchResponse = await fetch(getURL('stop', useLocalhost), {
            method: 'POST',
            body: body,
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            }
        })
        setWaitingForResponse(false);
        const status = fetchResponse.status
        if (status === 200) {
            alert("Stopped writing to " + time + ".mcap");
        }
        return status === 200
    }

    async function startRecording() {
        if(waitingForResponse) {
            return false
        }
        setWaitingForResponse(true);

        let body = '{ "time": ' + JSON.stringify(getFormattedDate()) + '}'
        // Creating the formatted date string
        const formattedDate = getFormattedDate()
        const fetchResponse = await fetch(getURL('start', useLocalhost), {
            method: 'POST',
            body: body,
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            }
        })

        setWaitingForResponse(false);
        const status = fetchResponse.status
        if (status === 200) {
            setTime(formattedDate)
        }
        return status === 200
    }

    async function toggleRecording() {
        if (recordingState.recording) {
            const stoppedRecording = await stopRecording()
            if (stoppedRecording) {
                await update()
            }
        } else {
            const startedRecording = await startRecording()
            if (startedRecording) {
                await update()
            }
        }
    }

    const updateRecording = (newRecordingState) => {
        setRecordingState((prevState) => ({
          ...prevState,
          recording: newRecordingState
        }));
      };

    return (
        <div className="centered-container">
            <button className={getButtonStyle()} onClick={toggleRecording} disabled={waitingForResponse}>
                {getButtonText()}
            </button>
        </div>
    )

}
