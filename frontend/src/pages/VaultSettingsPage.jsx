import { useState, useEffect } from 'react'
import { NavLink, useParams } from 'react-router-dom'


function VaultSettingsPage() {
    const params = useParams()
    const vault_id = Number(params.vault_id)
    const [isLoading, SetLoading] = useState(true)
    const [vault, SetVault] = useState({})    
    const [pinned, SetPinned] = useState()
    const [new_name, SetNewName] = useState('')
    const [
        error,
        message,
        showError,
        showMessage
    ] = useNotification()



    useEffect(() => {
        async function check_user_access() {
            const url = `/web/vaults/${vault_id}/status`
            const response = await fetch(
                url,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                }
            )
            const contentType = response.headers.get("content-type")
            if (response.ok) {
                // SetLoading(false)
                return true
            } else if (contentType && contentType.includes('application/json')){
                const response_data = await response.json()
                const response_error = response_data['detail'] || "No detail from server"
                console.log(response_error)
                document.location.href = '/vaults'
                return
            } else {
                const text = await response.text()
                const parser = new DOMParser()
                const nginx_document = parser.parseFromString(text, 'text/html')
                const nginx_error = nginx_document.title.slice(4)
                console.log(nginx_error)
                document.location.href = '/vaults'
                return
            }
        }
        async function get_vault_data() {
            const url = `/web/vaults/${vault_id}/info`
            const response = await fetch(
                url,
                {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )

            const contentType = response.headers.get("content-type")
            
            if (response.ok) {
                const response_data = await response.json()
                const vault = response_data['vault']
                SetVault(vault)
                SetPinned(vault['pinned'])
                await show_message( response_data['detail'])
            } else if (contentType && contentType.includes('application/json')){
                const response_data = await response.json()
                const response_error = response_data['detail'] || "No detail from server"
                await show_error(response_error)
                return
            } else {
                const text = await response.text()
                const parser = new DOMParser()
                const nginx_document = parser.parseFromString(text, 'text/html') 
                const nginx_error = nginx_document.title.slice(4)
                await show_error(nginx_error)
                return
            }
        }
    
        const access = check_user_access()
        if (access) {
            get_vault_data()
            SetLoading(false)
        } else {
            return
        }
    }, [])
        
    async function rename_backup(e) {
        e.preventDefault()

        const url = `/web/vaults/${vault_id}/rename`
        const response = await fetch(
                url,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(new_name.trim())
                }
            )
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            const response_data = await response.json()
            await get_vault_data()
            await show_message( response_data['detail'])
        } else if (contentType && contentType.includes('application/json')){
            const response_data = await response.json()
            const response_error = response_data['detail'] || "No detail from server"
            await show_error(response_error)
            return
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html') 
            const nginx_error = nginx_document.title.slice(4)
            await show_error(nginx_error)
            return
        }
        
    }


    async function delete_backup(e) {
        e.preventDefault()

        const url = `/web/vaults/${vault_id}`
        const response = await fetch(
                url,
                {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json"
                    }
                }
            )
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            document.location.href = '/vaults'                        
        } else if (contentType && contentType.includes('application/json')){
            const response_data = await response.json()
            const response_error = response_data['detail'] || "No detail from server"
            await show_error(response_error)
            return
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html') 
            const nginx_error = nginx_document.title.slice(4)
            await show_error(nginx_error)
            return
        }
        
    }


    return (



    )



}

export default VaultSettingsPage