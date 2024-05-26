import React from "react";

export function TextMetadataForm({metadata, setMetadata, index}) {

    function handleChange(e) {
        let newMetadata = metadata
        newMetadata.data[index] = e.target.value
        setMetadata(newMetadata)
    }

    return (
        <input value={metadata.data[index]} onChange={handleChange} className={"input input-bordered w-80"} disabled={false}/>
    )
}
