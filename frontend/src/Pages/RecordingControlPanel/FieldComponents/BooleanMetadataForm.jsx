import React from 'react';
import {stringToType} from '../../../Util/DataUtil';

export function BooleanMetadataForm({metadata, setMetadata, index}) {
    function handleChange(e) {
        let newMetadata = metadata
        newMetadata.data[index] = stringToType(e.target.value, 'boolean');
        setMetadata(newMetadata)
    }

    return (
        <select value={data[index] ? "True" : "False"} className={"select select-bordered w-80"}
                onChange={handleChange}>
            <option value={"False"}>False</option>
            <option value={"True"}>True</option>
        </select>
    )
}