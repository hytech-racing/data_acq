import React from 'react';
import {SectionTitle} from "./SectionTitle";
import {ErrorInfo} from "./ErrorInfo";

export function ErrorsList({errors}) {

    function getErrorRows() {
        let errorRows = []
        for (let i = errors.length - 1; i >= 0; i--) {
            errorRows.push(<ErrorInfo key={i} errors={errors} idx={i}/>);
        }
        return errorRows
    }

    return (
        <>
            <SectionTitle title={"Errors"}/>
            <div className={"join join-vertical"}>
                {getErrorRows()}
            </div>
        </>
    )
}