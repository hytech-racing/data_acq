import React, {useEffect, useState} from 'react';
import {getURL} from "../Util/ServerAddrUtil";

export function EditSSOT({metadata, setMetadata, useLocalhost}) {

    const metadataFiller = '[{"displayName":"Driver","name":"driver","options":[],"type":"string"},{"displayName":"Notes","name":"notes","options":[],"type":"string"},{"displayName":"Errors","name":"errors","options":[],"type":"string"}]'
    const [text, setText] = useState('');

    useEffect(() => {
        updateMetadata().then(response => {
            let newMetadata = metadata
            newMetadata.needUpdate = true
            newMetadata.fields = JSON.parse(response)
            setMetadata(newMetadata)
            setText(response)
        })
    }, [useLocalhost])

    async function updateMetadata() {
        let json;
        try {
            const fetchResponse = await fetch(getURL('fields', useLocalhost), {
                signal: AbortSignal.timeout(3000),
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            json = await fetchResponse.text()
        } catch (e) {
            json = metadataFiller
        }
        return JSON.stringify(JSON.parse(json), null, 4)
    }
    
    async function saveMetadata() {
        try {
            const fetchResponse = await fetch(getURL('saveFields', useLocalhost), {
                method: 'POST',
                body: JSON.stringify(JSON.stringify(JSON.parse(text), null, 4)),
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                }
            })
        } catch (e) {
            alert(e)
        }

        updateMetadata().then(response => {
            let newMetadata = metadata
            newMetadata.needUpdate = true
            newMetadata.fields = JSON.parse(response)
            setMetadata(newMetadata)
            setText(response)
        })
    }

    return (
        <>
            <main>
                <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                    <textarea className={"textarea textarea-bordered w-80 h-[60dvh] resize-none"} value={text}
                              onChange={e => setText(e.target.value)} wrap={'off'}></textarea>
                </div>
            </main>
            <footer className={"sticky bottom-0 bg-base-100"}>
                <div className={"flex flex-row gap-2 pt-4"}>
                    <div className={"grow w-max"}/>
                    <button className={"btn"} onClick={() => updateMetadata().then(response => {
                        let newMetadata = metadata
                        newMetadata.needUpdate = true
                        newMetadata.fields = JSON.parse(response)
                        setMetadata(newMetadata)
                        setText(response)
                    })}>
                        Reset
                    </button>
                    <button className={"btn btn-success"} onClick={saveMetadata}>
                        Save
                    </button>
                    <div className={"grow w-max"}/>
                </div>
            </footer>
        </>
    )

}