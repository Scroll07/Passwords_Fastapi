import {sleep} from '../utils/sleep.js'

export async function show_error(SetError, error_text) {
        SetError(error_text)
        await sleep(3500)
        SetError('')
    }
export async function show_message(SetMessage, message_text) {
        SetMessage(message_text)
        await sleep(3500)
        SetMessage('')
    }
