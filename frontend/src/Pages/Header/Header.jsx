import React, { useState } from 'react';
import {PageTitle} from "./PageTitle";
import {HeaderLink} from "./HeaderLink";
import {AddrToggle} from "./AddrToggle";

export function Header({currPanel, setCurrPanel, useLocalhost, setUseLocalhost}) {
    return (
        <div className={"navbar bg-base-100 items-center justify-center pb-6"}>
            <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                <AddrToggle useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>
                <PageTitle text={"HyTech"}></PageTitle>

                <ul className={"menu menu-horizontal bg-base-200 rounded-box"}>
                    <HeaderLink currPanel={currPanel} setCurrPanel={setCurrPanel} panel={"Recording"}/>
                    <HeaderLink currPanel={currPanel} setCurrPanel={setCurrPanel} panel={"Params"}/>
                    <HeaderLink currPanel={currPanel} setCurrPanel={setCurrPanel} panel={"Edit SSOT"}/>
                </ul>
            </div>
        </div>
    )
}