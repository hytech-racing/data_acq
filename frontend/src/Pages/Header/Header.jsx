import React, { useState } from 'react';
import {PageTitle} from "./PageTitle";
import {HeaderLink} from "./HeaderLink";
import {AddrToggle} from "./AddrToggle";

export function Header({title, useLocalhost, setUseLocalhost}) {
    return (
        <div className={"navbar bg-base-100 items-center justify-center pb-6"}>
            <div className={"flex flex-col gap-4 items-center justify-center pt-6"}>
                <AddrToggle useLocalhost={useLocalhost} setUseLocalhost={setUseLocalhost}/>
                <PageTitle text={title}></PageTitle>

                <ul className={"menu menu-horizontal bg-base-200 rounded-box"}>
                    <HeaderLink link={"/"} name={"Recording"}/>
                    <HeaderLink link={"ssot"} name={"Edit SSOT"}/>
                </ul>

            </div>
        </div>
    )
}