import React from "react";

export function TextForm({params, setParams, fieldName}) {

    function handleChange(e) {
        let newParams = params
        params[fieldName].value = e.target.value
        setParams(newParams)
    }

    return (
        <input value={params[fieldName].value} onChange={handleChange} className={"input input-bordered w-80"}/>
    )
}
