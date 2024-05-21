import React from 'react';
import {TextForm} from "./TextForm";
import {FieldTitle} from "./FieldTitle";
import {BooleanForm} from "./BooleanForm";

export function Field({params, setParams, fieldName}) {
    
    function getField() {
        let type = params[fieldName].type
        if (type === 'number') {
            return (
                <TextForm params={params} setParams={setParams} fieldName={fieldName}/>
            )
        } else if (type === 'bool') {
            return (
                <BooleanForm params={params} setParams={setParams} fieldName={fieldName}/>
            )
        } else {
            return (
                <></>
            )
        }
    }

    return (
        <>
            <FieldTitle fieldName={fieldName}/>
            {getField()}
        </>
    )
}