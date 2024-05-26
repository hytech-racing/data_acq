import React from 'react';
import {TextMetadataForm} from "./FieldComponents/TextMetadataForm";
import {FieldTitle} from "./FieldComponents/FieldTitle";
import {DropdownMetadataForm} from "./FieldComponents/DropdownMetadataForm";
import {BooleanMetadataForm} from "./FieldComponents/BooleanMetadataForm";

export function Field({metadata, setMetadata, index}) {
    
    function getField() {
        if (metadata.fields[index] === undefined) {
            return (<></>)
        } else if (metadata.fields[index].type === "boolean") {
            return (<BooleanMetadataForm metadata={metadata} setData={setMetadata} index={index}/>)
        } else if(metadata.fields[index].options.length > 0) {
            return (<DropdownMetadataForm metadata={metadata} setMetadata={setMetadata} index={index}/>)
        } else {
            return (<TextMetadataForm metadata={metadata} setMetadata={setMetadata} index={index}/>)
        }
    }

    return (
        <>
            <FieldTitle metadata={metadata} index={index}/>
            {getField()}
        </>
    )
}