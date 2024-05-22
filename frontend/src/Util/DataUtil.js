import {getFormattedDate} from "./DateUtil";

export function getDefaultData(fields) {
    console.log(fields)
    let data = []
    for (let i = 0; i < fields.length; i++) {
        data.push(getDefaultValue(fields[i].type))
    }
    return data
}

function getDefaultValue(type) {
    if (type === 'string') {
        return ''
    } else if (type === 'boolean') {
        return false
    } else if (type === 'pid') {
        return {p: '', i: '', d: ''}
    }
    return null
}

export function getMetadata(fields, data, startTime) {
    let body = "{ "
    for (let i = 0; i < fields.length; i++) {
        if (fields[i].type === "string") {
            body += '"' + fields[i].name + '": ' + JSON.stringify(data[i])
        } else {
            body += '"' + fields[i].name + '": ' + JSON.stringify(JSON.stringify(data[i]))
        }
        body += ', '
    }
    body += '"startTime": ' + JSON.stringify(startTime) + ","
    body += '"endTime": ' + JSON.stringify(getFormattedDate())
    body += " }"
    return body;
}