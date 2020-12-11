window.addEventListener('load', () => {
  const POST = document.querySelector('#post-article')
  const DOMAIN =  window.location.origin

  function updateInteraction(url, payload){
    xhr = new XMLHttpRequest();
    xhr.open('POST',url, true);
    xhr.onreadystatechange = function(){
      if(xhr.readyState == 4){
        if(xhr.status == 200){
          console.log(xhr.responseText);
        } else {
          console.log("error");
        }
      }
    }
    xhr.send(payload);
  }

  if (POST) {
      const SESSION_ID = POST.dataset.sessionId

      if (SESSION_ID !== 'null') {
          let minutes = 0
          setTimeout(() => {
              let form = new FormData()
              form.append('minutes', 0)
              const URI = `${DOMAIN}/posts/interaction/${SESSION_ID}/edit/`
              updateInteraction(URI, form);
          }, 5000)

          let requestInterval = setInterval(() => {
              let form = new FormData()
              if(minutes >= 20) {
                  clearInterval(requestInterval)
              }
              minutes = minutes + 1
              form.append('minutes', minutes)
              const URI = `${DOMAIN}/posts/interaction/${SESSION_ID}/edit/`
              updateInteraction(URI, form);
          }, (60 * 1000))
      }
  }
})
