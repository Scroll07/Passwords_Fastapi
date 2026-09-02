import {sleep} from '../utils/sleep.js'

async function show_error(error_text) {
        SetError(error_text)
        await sleep(3500)
        SetError('')
    }
async function show_message(message_text) {
        SetMessage(message_text)
        await sleep(3500)
        SetMessage('')
    }

export default {show_error, show_message}