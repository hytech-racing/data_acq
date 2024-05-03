import React, {useEffect, useState} from 'react';
import {FileInfo} from "../Components/FileInfo";
import {PageTitle} from "../Components/PageTitle";
import {AddrToggle} from "../Components/AddrToggle";
import {getURL} from "../Util/ServerAddrUtil";

export function Files({}) {

    const [useLocalhost, setUseLocalhost] = useState(false)
    const [fileData, setFileData] = useState([])

    const [offloaded, setOffloaded] = useState([])
    const [notOffloaded, setNotOffloaded] = useState([])

    const [internetConnection, setInternetConnection] = useState(false)

    const awsAddr = 'http://54.243.4.174:8080/'

    async function checkInternet() {
        try {
            const fetchResponse = await fetch(awsAddr, {
                signal: AbortSignal.timeout(1000),
            })
            let json = await fetchResponse.text()
            return json === 'Hello, World!'
        } catch (e) {
            return false
        }
    }

    async function updateFiles(hasInternet) {
        if (hasInternet) {

        } else {
            try {
                const fetchResponse = await fetch(getURL('all_files'), {
                    signal: AbortSignal.timeout(3000)
                })
                // TODO
            } catch (e) {
                // TODO
            }
        }
    }

    useEffect(() => {
        updateFiles().then(fileData => setFileData(fileData))
    }, [])

    return (
        <main>
            <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                <AddrToggle useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>
                
                <div className={"flex"}>
                    <PageTitle text={"MCAP Files on Car"}/>
                </div>

                {fileData.map((file, index) => <FileInfo key={file.name} fileData={fileData} index={index} useLocalhost={useLocalhost}/>)}
            </div>
        </main>
    )

}