function stripDateDetails(givenDate){
    if(givenDate.getMinutes() > 45){
        givenDate.setMinutes(0);
        givenDate.setHours(givenDate.getHours() + 1);
    }else if(givenDate.setMinutes() < 15){
        givenDate.setMinutes(0);
    }else{
        givenDate.setMinutes(30);
    }
    givenDate.setSeconds(0)
}
CACHE = {}

function baseURL(){
    var getUrl = window.location;
    return getUrl .protocol + "//" + getUrl.host + "/" ;
}

function getCookie(name){
    var cookieValue = null;
    if(document.cookie && document.cookie != ''){
        var cookies = document.cookie.split(';');
        for(var i =0; i < cookies.length; i++){
            var cookie = cookies[i].trim();
            if(cookie.substring(0, name.length+1) === (name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length+1));
                break
            }
        }
    }
    return cookieValue
}

function combineDict(dict1, dict2){
    var newdict = {}
    Object.keys(dict1).forEach(function(key){
        newdict[key] = dict2[key]
    })
    Object.keys(dict2).forEach(function(key){
        newdict[key] = dict2[key]
    })
    return newdict;
}

function getData(url, header){
    var cacheHas = false;
    var attribute = ""
    Object.keys(header).forEach(function(key){
        attribute += key + header[key];
    })
    Object.keys(CACHE).forEach(function(key){
        if(key == attribute){
            cacheHas = truel
        }
    })
    if(cacheHas){
        return CACHE[attribute];
    }
    var headers = {
        'csrftoken' : getCookie("csrftoken"), "data_type" : attribute
    }
    headers = combineDict(headers, header)
    return $.get(baseURL() + url, headers, function(data){
        var result = JSON.parse(data);
        CACHE[attribute] = result;
        return result;
    })
}