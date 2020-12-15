window.addEventListener('load', function(){
  var POST = document.querySelector('#post-article')
  var DOMAIN =  window.location.origin

  function updateInteraction(url, payload){
    var xhr = new XMLHttpRequest();
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
      var SESSION_ID = POST.dataset.sessionId

      if (SESSION_ID !== 'null') {
          var minutes = 0
          setTimeout(function() {
              var form = new FormData();
              form.append('minutes', 0);
              var uri = DOMAIN + '/posts/interaction/' + SESSION_ID + '/edit/';
              updateInteraction(uri, form);
          }, 5000)

          var requestInterval = setInterval(function() {
              var form = new FormData();
              if(minutes >= 20) {
                  clearInterval(requestInterval)
              }
              minutes = minutes + 1;
              form.append('minutes', minutes);
              var uri = DOMAIN + '/posts/interaction/' + SESSION_ID + '/edit/';
              updateInteraction(uri, form);
          }, (60 * 1000))
      }
  }
})
