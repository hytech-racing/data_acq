import React from 'react';

export function BooleanForm({params, setParams, fieldName}) {

    function handleChange(e) {
        let newParams = params
        params[fieldName].value = e.target.value
        setParams(newParams)
    }

    return (
        <select value={params[fieldName].value} className={"select select-bordered w-80"} onChange={handleChange}>
            <option value={"on"}>On</option>
            <option value={"off"}>Off</option>
        </select>
    )

}