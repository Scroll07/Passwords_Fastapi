import { useState, useEffect } from "react"
import { NavLink } from "react-router-dom"

function CreateVaultPage() {
    const [vaultName, setVaultName] = useState('') 
    const [vaultPassword, setVaultPassword] = useState('') 
    const [error, setError] = useState('')


    function validate_data() {
        let validate_error = null
        const clearName = vaultName.trim()
        const clearPassword = vaultPassword.trim()

        if (! (0 < clearName.length < 33)) {
            validate_error = 'Wrong length of vault name'    
        } else if (! (0 < clearPassword.length < 33)) {
            validate_error = 'Wrong length of vault password'    
        } else if (clearPassword.includes(' ')) {
            validate_error = 'Master Password must not contain any spaces'
        }

        return {
            "name": clearName,
            "master_password": clearPassword,
            "error": validate_error
        }
    }
    
    async function createRequest() {
        const validate_data = validate_data()
        if (validate_data['error']) {
            setError(validate_data['error'])
            return
        }

        const url = '/web/vaults/create'
        const response = await fetch(
            url,
            {
                method: "POST",
                headers: {
                    "content-type": "application/json"
                },
                body: JSON.stringify({
                    "vault_name": validate_data['name'],
                    "vault_master_password": validate_data['master_password'] 
                })
            }
        )
        const contentType = response.headers.get("content-type")

        if (response.ok) {
            document.location.href = '/vaults'
        } else if (contentType && contentType.includes("application/json")) {
            const response_data = await response.json()
            const server_message = response_data['detail']
            SetAccess(false)
            SetError(server_message)
        } else {
            const text = await response.text()
            const parser = new DOMParser()
            const nginx_document = parser.parseFromString(text, 'text/html') 
            const nginx_error = nginx_document.title.slice(4)
            SetError(nginx_error)
            return  
        }

    }

    return (
        // H1 Create Vault
        // Кнопка назад к /vaults
        // ФОРМА ДЛЯ СОЗДАНИЯ VAULT С КНОПКОЙ
    )

}

export default CreateVaultPage