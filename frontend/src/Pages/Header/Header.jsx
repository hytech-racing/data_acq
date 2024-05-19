import React, { useState } from 'react';
import {PageTitle} from "./PageTitle";
import {HeaderLink} from "./HeaderLink";
import {AddrToggle} from "./AddrToggle";

export function Header({title, useLocalhost, setUseLocalhost}) {
    return (
        <div className={"navbar bg-base-100 items-center justify-center"}>
            <div className={"flex flex-col items-center justify-center pt-6"}>
                <AddrToggle useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>
                <PageTitle text={title}></PageTitle>

                <div className={"flex flex-row pt-3"}>
                            <HeaderLink link={"/"} name={"MCAPRecorder"}/>
                            <HeaderLink link={"ssot"} name={"Edit SSOT"}/>
                </div>

            </div>
        </div>
    )
}