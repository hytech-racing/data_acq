import React, {useEffect, useState} from "react";
import {stringToType} from '../../../Util/DataUtil'

export function DropdownMetadataForm({metadata, setMetadata, index}) {

    function handleChange(e) {
        let newMetadata = metadata
        newMetadata.data[index] = stringToType(e.target.value, newMetadata.fields[index].type);
        setMetadata(newMetadata)
    }

    return (
        <select value={data[index]} className={"select select-bordered w-80"} onChange={handleChange}
                disabled={false}>
            {metadata.fields[index].options.map((option) => <option value={option}>{option}</option>)}
        </select>
    )

}

