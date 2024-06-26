import React from 'react'
import { exec } from "node:child_process";

export function OffloadButton() {

    const webserverURL: string = 'http://192.168.203.1:6969'

    async function offload() {
        const fetchResponse = await fetch(webserverURL + '/offload', {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json'
            }
        })
        const status = fetchResponse.status
        return status === 200
    }

    return (
        <button className={"btn"} onClick={offload} disabled={false}>
            Offload
        </button>
    )
}
