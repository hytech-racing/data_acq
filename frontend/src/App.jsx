import React, {useEffect, useState} from 'react';
import './App.css';
import {BrowserRouter, Routes, Route} from "react-router-dom";
import {MCAPRecorder} from "./Pages/MCAPRecorder";
import {EditSSOT} from "./Pages/EditSSOT";
import {Files} from "./Pages/Files"
import {Header} from "./Pages/Header/Header"
import {RecordingControlPanel} from "./Pages/RecordingControlPanel/RecordingControlPanel";

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path={"/"}>
                    <Route index element={<RecordingControlPanel/>}/>
                    <Route path={"files"} element={<Files/>}/>
                    <Route path={"ssot"} element={<EditSSOT/>}/>
                </Route>
            </Routes>
        </BrowserRouter>
    )
}


export default App;
