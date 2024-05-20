import React from 'react';

export function SectionTitle({title}) {
    return (
        <div className={"flex flex-row w-96"}>
            <article className={"prose"}>
                <h3>
                    {title}:
                </h3>
            </article>
            <div className={"grow w-max"}/>
        </div>
    )
}