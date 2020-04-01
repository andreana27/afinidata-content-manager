(() => {
    window.addEventListener('load', () => {

        const POST = document.querySelector('#post-article')
        const DOMAIN =  window.location.origin

        console.log(DOMAIN)

        if (POST) {
            const SESSION_ID = POST.dataset.sessionId
            console.log(POST)

            if (SESSION_ID !== 'null') {
                let minutes = 0

                setTimeout(() => {
                    let form = new FormData()
                    form.append('minutes', 0)
                    const URI = `${DOMAIN}/posts/interaction/${SESSION_ID}/edit/`
                    fetch(URI, {
                        method: 'post',
                        body: form
                    })
                        .then(response => response.json())
                        .then(response => console.log(response))
                }, 5000)
                let requestInterval = setInterval(() => {
                    let form = new FormData()
                    console.log(minutes)
                    if(minutes >= 20) {
                        clearInterval(requestInterval)
                    }
                    minutes = minutes + 1
                    form.append('minutes', minutes)
                    const URI = `${DOMAIN}/posts/interaction/${SESSION_ID}/edit/`
                    console.log(URI)
                    fetch(URI, {
                        method: 'post',
                        body: form
                    })
                        .then(response => response.json())
                        .then(response => console.log(response))
                }, (60 * 1000))
            }
        }
    })
})()