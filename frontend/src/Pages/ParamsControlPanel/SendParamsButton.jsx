import React from 'react';
import {NetworkingUtils} from "../../Util/NetworkingUtils";

export function SendParamsButton({params, useLocalhost, updateParams}) {

    const [waitingForResponse, setWaitingForResponse] = React.useState(false);

    async function sendParams() {
        if(waitingForResponse) {
            return
        }
        const response = await NetworkingUtils.postRequest(NetworkingUtils.getURL(['params'], useLocalhost), params)
        if(response.success) {
            alert("Params successfully sent")
            updateParams()
        } else {
            alert("Failed to send params: " + response.response)
        }
    }

    return (
        <div className={"centered-container"}>
            <button className={"btn btn-success"} onClick={sendParams}>
                Send Parameters
            </button>
        </div>
    )

}