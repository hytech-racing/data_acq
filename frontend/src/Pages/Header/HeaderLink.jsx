import React from 'react';

export function HeaderLink({currPanel, setCurrPanel, panel}) {

    function getStyle() {
        if(currPanel === panel) {
            return "btn btn-primary"
        }
        return "btn"
    }

    return (
        <li>
            <button className={getStyle()} onClick={() => setCurrPanel(panel)}>
                {panel}
            </button>
        </li>
    )

}