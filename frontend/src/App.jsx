import React, {useEffect, useState} from 'react';
import './App.css';
import {BrowserRouter, Routes, Route} from "react-router-dom";
import {MCAPRecorder} from "./Pages/MCAPRecorder";
import {EditSSOT} from "./Pages/EditSSOT";
import {Files} from "./Pages/Files"
import {Header} from "./Pages/Header/Header"

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path={"/"}>
                    <Route index element={<MCAPRecorder/>}/>
                    <Route path={"files"} element={<Files/>}/>
                    <Route path={"ssot"} element={<EditSSOT/>}/>
                </Route>
            </Routes>
        </BrowserRouter>
    )
}


export default App;
