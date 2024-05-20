export function getURL(route, useLocalhost) {
    let ret = ''
    if (useLocalhost) {
        ret += 'http://localhost:8888'
    } else {
        ret += 'http://192.168.203.1:8888'
    }
    ret += '/'
    ret += route
    return ret
}