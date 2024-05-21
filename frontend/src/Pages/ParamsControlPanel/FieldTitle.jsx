import React from 'react';

export function FieldTitle({fieldName}) {

    return (
        <div className={"flex flex-row items-center w-80 -mb-3"}>
            <article className={"prose"}>
                <h4>{fieldName}:</h4>
            </article>
            <div className={"grow w-max"}/>
        </div>
    )

}