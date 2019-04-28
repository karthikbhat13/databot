
var sessionDone = 1;
var submit = function(){
    input = document.getElementById("userInput").value
    document.getElementById("userInput").value = ''
    console.log(input)
    createResponse('user', input);
    greeting_flag = false
    greetings = ["hi", "hey", "hello", "greetings"]
    greetings.forEach(element => {
        if(element == input.toLowerCase()){
            createResponse('bot', "Hi! How may I help you?", 1);
            greeting_flag = true
            return;
        }
    });

    if(!greeting_flag){
        greeting_flag = false;
        var xhr = new XMLHttpRequest()
        xhr.open('POST', 'http://localhost:5000/user_input', true)
        xhr.setRequestHeader('Content-type' , 'application/x-www-form-urlencoded')

        xhr.send('user_input='+input+'&sessionDone='+String(sessionDone))
        xhr.timeout = 30000;
        xhr.onload = function(){
            if(xhr.readyState == 4 && xhr.status == 200){
                resp = JSON.parse(xhr.response)
                console.log(resp.text)
                sessionDone = parseInt(resp['sessionDone'])
                console.log(sessionDone)
                if(resp.text.length > 0)
                    createResponse('bot', resp.text, sessionDone)
                else
                {
                    sessionDone = 1;
                    createResponse('bot', "Sorry, we could not find appropriate response for you", sessionDone);
                }
            }
        }

        xhr.ontimeout = function(){
            sessionDone = 1;
            createResponse('bot', "Sorry, something went wrong. Request has timed out", sessionDone);
        }

        xhr.onerror = function(){
            sessionDone = 1
            createResponse('bot', "Sorry, something went wrong. We encountered an error.", sessionDone)
        }
    }
    
}

var createResponse = function(type, text, sd){
    console.log(type);
    console.log(text);
    console.log(sd)
    if(type == 'bot'){
        var div = document.createElement('div')
        div.setAttribute('class', 'container')

        var img = document.createElement('img')
        img.setAttribute('src', '/assets/bot.png')
        img.setAttribute('style', 'width=100%;')
        img.setAttribute('alt', 'Bot')
        img.setAttribute('class', 'left')

        var par = document.createElement('p')
        if(sd == 0){
            prefix = "Hey, your query fetched multiple results.\nHelp us narrow down, can you tell me about "
            suffix = "\n You can also choose to see all by typing 'show all' \nor try one more column by typing 'idk'"
            par.innerHTML = prefix+text+suffix
            
        }
        else{
            par.innerHTML = text
        }
        par.setAttribute('class', 'bot')
        
        var span = document.createElement('span')
        span.setAttribute('class', 'time-left')
        
        var d = new Date()

        var h = d.getHours()
        var min = d.getMinutes()

        span.innerHTML = String(h) + ':' +String(min)

        div.appendChild(img);
        div.appendChild(par)
        div.appendChild(span)

        document.getElementById('body').appendChild(div);
    }

    else{
        var div = document.createElement('div')
        div.setAttribute('class', 'container darker')

        var img = document.createElement('img')
        img.setAttribute('src', '/assets/user.png')
        img.setAttribute('style', 'width=100%;')
        img.setAttribute('alt', 'User')
        img.setAttribute('class', 'right')

        var par = document.createElement('p')
        par.innerHTML = text
        par.setAttribute('class', 'user')
        
        var span = document.createElement('span')
        span.setAttribute('class', 'time-right')
        
        var d = new Date()

        var h = d.getHours()
        var min = d.getMinutes()

        span.innerHTML = String(h) + ':' +String(min)

        div.appendChild(img);
        div.appendChild(par)
        div.appendChild(span)

        document.getElementById('body').appendChild(div)
    }
}