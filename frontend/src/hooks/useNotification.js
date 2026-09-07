import { useState } from 'react'

export function useNotification() {
    const [error, setError] = useState('')
    const [message, setMessage] = useState('')

    function showError(text) {
        setError(String(text))
        setTimeout(() => {
            setError('')
        }, 3500)
    }

    function showMessage(text) {
        setMessage(String(text))
        setTimeout(() => {
            setMessage('')
        }, 3500)
    }

    return [
        error, 
        message,
        showError,
        showMessage
    ]
}
