export class NetworkingUtils {

    /**
     * Makes a get request
     * @param url request url
     * @param filler value to return if request fails
     * @param maxWait maximum wait time before timeout in ms (default: 3000)
     * @returns Result of the get request
     */
    static async getRequest(url, filler, maxWait=3000) {
        try {
            const fetchResponse = await fetch(url, {
                signal: AbortSignal.timeout(maxWait),
                method: 'GET',
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            let json = await fetchResponse.text()
            return JSON.parse(json)
        } catch (e) {
            return filler
        }
    }

    /**
     * Makes a post request
     * @param url request url
     * @param body request body
     * @param maxWait maximum wait time before timeout in ms (default: 3000)
     * @returns Object with success and response
     */
    static async postRequest(url, body, maxWait=3000) {
        try {
            const fetchResponse = await fetch(url, {
                signal: AbortSignal.timeout(maxWait),
                method: 'POST',
                body: body,
                headers: {
                    Accept: 'application/json',
                    'Content-Type': 'application/json'
                }
            })
            const status = fetchResponse.status
            const json = await fetchResponse.text()
            return {success: status === 200, response: JSON.parse(json)}
        } catch (e) {
            return {success: false, response: 'Fetch failed'}
        }
    }

    static getURL(route, useLocalhost) {
        let ret = ''
        if (useLocalhost) {
            ret += 'http://localhost:6969'
        } else {
            ret += 'http://192.168.203.1:6969'
        }
        for (let r in route) {
            ret += '/'
            ret += r
        }
        return ret
    }

}