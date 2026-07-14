import { NavLink, Outlet } from "react-router-dom"
import HeaderLayout from "./HeaderLayout"
import FooterLayout from "./FooterLayout"

import './BaseLayout.css'

function BaseLayout() {
    return (
        <>
            <HeaderLayout />
            <Outlet />
            <FooterLayout />
        </>
    )
}

export default BaseLayout