import React from "react";
import { useState } from "react";
import {getURL} from "../../Util/ServerAddrUtil";
import {getFormattedDate} from "../../Util/DateUtil";
import {getMetadata} from "../../Util/DataUtil";
import {wait} from "@testing-library/user-event/dist/utils";

export function StartStopButton({recording, setRecording, useLocalhost, update}) {

    const [waitingForResponse, setWaitingForResponse] = useState(false);

    function getButtonStyle() {
        return recording ? "btn btn-error" : "btn btn-success"
    }

    function getButtonText() {
        if (waitingForResponse) {
            return "..."
        }
        return recording ? "Stop Recording" : "Start Recording"
    }

    async function stopRecording() {
        if(waitingForResponse) {
            return false
        }
        setWaitingForResponse(true);

        const fetchResponse = await fetch(getURL('stop', useLocalhost), {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            }
        })
        setWaitingForResponse(false);
        const status = fetchResponse.status
        return status === 200
    }

    async function startRecording() {
        if(waitingForResponse) {
            return false
        }
        setWaitingForResponse(true);

        const fetchResponse = await fetch(getURL('start', useLocalhost), {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            }
        })

        setWaitingForResponse(false);
        const status = fetchResponse.status
        return status === 200
    }

    async function toggleRecording() {
        if (recording) {
            const stoppedRecording = await stopRecording()
            if (stoppedRecording) {
                setRecording(false)
                update()
            }
        } else {
            const startedRecording = await startRecording()
            if (startedRecording) {
                setRecording(true)
                update()
            }
        }
    }

    return (
        <div className="centered-container">
            <button className={getButtonStyle()} onClick={toggleRecording} disabled={waitingForResponse}>
                {getButtonText()}
            </button>
        </div>
    )

}
