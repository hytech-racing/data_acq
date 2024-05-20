import React from 'react'
import {getURL} from "../Util/ServerAddrUtil";

export function OffloadButton() {

    async function offload() {
        const fetchResponse = await fetch(getURL('offload', useLocalhost), {
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

        <button className={"btn"} onClick={() => alert("New Alert")} disabled={false}>
            Offload
        </button>
    )
}
