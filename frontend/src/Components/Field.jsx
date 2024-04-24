import React from 'react';
import {TextForm} from "./TextForm";

export function Field({fields, data, setData, index, recording}) {
    
    function getField() {
        //console.log(JSON.stringify(fields[index]))
        if (fields[index] === undefined) {
            return (<></>)
        } else if (fields[index].automatic) {
            return (<></>)
        } else if(fields[index].dropdown) {
            return (<></>)
        } else {
            return (<TextForm fields={fields} data={data} setData={setData} index={index} recording={recording}/>)
        }
    }

    return (
        <>
            {getField()}
        </>
    )
}