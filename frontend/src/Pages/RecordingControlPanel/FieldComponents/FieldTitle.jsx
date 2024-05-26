import React from 'react';

export function FieldTitle({metadata, index}) {

    return (
        <div className={"flex flex-row items-center w-80 -mb-3"}>
            <article className={"prose"}>
                <h4>{metadata.fields[index].displayName}:</h4>
            </article>
            <div className={"grow w-max"}/>
        </div>
    )

}