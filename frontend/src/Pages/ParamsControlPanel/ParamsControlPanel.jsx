import React, {useEffect} from 'react';
import {NetworkingUtils} from "../../Util/NetworkingUtils";
import {Field} from "./Field";
import {SendParamsButton} from "./SendParamsButton";

export function ParamsControlPanel({params, setParams, useLocalhost}) {

    const paramsFiller = {
        param1: {type: 'number', value: '0.0'},
        param2: {type: 'number', value: '1.0'},
        param3: {type: 'bool', value: 'on'}}

    async function updateParams() {
        NetworkingUtils.getRequest(NetworkingUtils.getURL(['params'], useLocalhost), paramsFiller).then((response) => {
            setParams(response)
        })
    }

    useEffect(() => {
        updateParams().then()
    }, [useLocalhost])

    function getFields() {
        let fields = []
        for (const [key, value] of Object.entries(params)) {
            fields.push(<Field key={key} params={params} setParams={setParams} fieldName={key}/>)
        }
        return fields
    }

    return (
        <div className={"flex flex-col gap-4 items-center justify-center"}>
            {getFields()}
            <SendParamsButton params={params} useLocalhost={useLocalhost} updateParams={updateParams}/>
        </div>
    )
}