import React from "react";

export function TextForm({fields, data, setData, index, recording}) {

    function handleChange(e) {
        // TODO: validate input
        setData(data.map((v, i) => i === index ? e.target.value : v))
    }

    return (
        <>
            <div className={"flex flex-row items-center w-80"}>
                <article className={"prose"}>
                    <h4>{fields[index].displayName}:</h4>
                </article>
                <div className={"grow w-max"}/>
            </div>
            <input value={data[index]} onChange={handleChange} className={"input input-bordered w-80 -mt-3"} disabled={recording}/>
        </>
    )
}
