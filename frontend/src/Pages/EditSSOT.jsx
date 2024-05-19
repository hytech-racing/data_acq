import React, {useEffect, useState} from 'react';
import {AddrToggle} from "../Components/AddrToggle";
import {PageTitle} from "../Components/PageTitle";
import {getURL} from "../Util/ServerAddrUtil";

export function EditSSOT({}) {

    const [useLocalhost, setUseLocalhost] = useState(false)
    const [metadata, setMetadata] = useState('')

    useEffect(() => {
        updateMetadata().then(metadata => setMetadata(metadata))
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
            //alert("WARNING: Using hardcoded fields")
            json = '[{"name":"driver","displayName":"Driver","type":"string","automatic":false,"options":["Shayan","Ryan"]},{"name":"testingGoal","displayName":"Testing Goal","type":"string","automatic":false,"options":[]}]'
        }
        return JSON.stringify(JSON.parse(json), null, 4)
    }
    
    async function saveMetadata() {
        try {
            const fetchResponse = await fetch(getURL('saveFields', useLocalhost), {
                method: 'POST',
                body: JSON.stringify(JSON.stringify(JSON.parse(metadata), null, 4)),
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                }
            })
        } catch (e) {
            alert(e)
        }
        
        updateMetadata().then(metadata => setMetadata(metadata))
    }

    return (
        <>
            <main>
                <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                    <AddrToggle useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>
                    <div className={"flex"}>
                        <PageTitle text={"Metadata Editor"}/>
                    </div>
                </div>

                <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                    <textarea className={"textarea textarea-bordered w-80 h-[70dvh] resize-none"} value={metadata}
                              onChange={e => setMetadata(e.target.value)} wrap={'off'}></textarea>
                </div>
            </main>
            <footer className={"sticky bottom-0 bg-base-100"}>
                <div className={"flex flex-row gap-4 pt-6"}>
                    <div className={"grow w-max"}/>
                    <button className={"btn"} onClick={() => updateMetadata().then(metadata => setMetadata(metadata))}>
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