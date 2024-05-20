import React from 'react';
import {Link} from "react-router-dom";

export function HeaderLink({link, name}) {

    return (
        <li>
            <Link to={link} className={"pl-4 pr-4"}>
                <article className={"prose"}>
                    <h5>
                        {name}
                    </h5>
                </article>
            </Link>
        </li>
    )

}