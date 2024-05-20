import React from 'react';
import {SectionTitle} from "./SectionTitle";
import {ErrorInfo} from "./ErrorInfo";

export function ErrorsList({errors}) {
    return (
        <>
            <SectionTitle title={"Errors"}/>
            <div className={"join join-vertical"}>
                <ErrorInfo/>
                <ErrorInfo/>
                <ErrorInfo/>
                <ErrorInfo/>
                <ErrorInfo/>
            </div>
        </>
    )
}