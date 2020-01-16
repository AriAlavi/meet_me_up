function stripDateDetails(givenDate){
    if(givenDate.getMinutes() > 45){
        givenDate.setMinutes(0);
        givenDate.setHours(givenDate.getHours() + 1);
    }else if(givenDate.getMinutes() < 15){
        givenDate.setMinutes(0);
    }else{
        givenDate.setMinutes(30);
    }
    givenDate.setSeconds(0)
    return givenDate
}
function datetimeToDate(givenDateTime){
    givenDateTime.setSeconds(0);
    givenDateTime.setMinutes(0);
    givenDateTime.setHours(0)
    return givenDateTime
}
CACHE = {}

function dateToPython(givenDate){
    var m = givenDate.getMonth() + 1;
    var d = givenDate.getDate();
    var y = givenDate.getFullYear();
    return m + "/" + d + "/" + y;
}
const MONTHS_ABV = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
const DAY_ABV = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

function formatDate(givenDate){
    var d = givenDate.getDate();
    var day = DAY_ABV[givenDate.getDay()];
    return day + " " + d;
}
function formatDateDetailed(givenDate){
    var m = MONTHS_ABV[givenDate.getMonth()];
    var d = givenDate.getDate();
    var day = DAY_ABV[givenDate.getDay()];
    return day + ", " + m + " " + d 
}

function formatTime(givenTime){
    var minutes = String(givenTime.getMinutes());
    if(minutes.length == 1){
        minutes += "0"
    }
    var ending = "am";
    var hours = givenTime.getHours();
    if(hours == 0 && minutes == "00"){
        return "midnight"
    }
    else if(hours == 12){
        ending = "pm";
    }
    else if(hours == 0){
        hours = 12;
    }
    else if(hours > 12){
        ending = "pm"
        hours -= 12;
    }
    return String(hours) + ":" +minutes +" " + ending;

}

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

// Example call: getData("freeInterface", {"data_type" : "getFree", "start_date" : s, "end_date" : e}).then(function(e){console.log(e)})

async function getData(url, header){
    var cacheHas = false;
    var hash = "";
    Object.keys(header).forEach(function(key){
        hash += key + header[key];
    })
    var cacheValue = CACHE[hash];
    if(cacheValue != undefined){
        return cacheValue;
    }
    var localHeaders = header;
    localHeaders["csrfmiddlewaretoken"] = getCookie("csrftoken");
    var result = null;
    var callresult = $.get(baseURL() + url, header, function(data){
        CACHE[hash] = data;
        return data;
    })
    return callresult;

}

function dateDifference(date1, date2){
    return (date1 - date2) / 86400000
}

function createTable(start_date, date_range, end_date, parent, min_start, min_end){
    function timeDescriptionGet(start_date, end_date){
        return formatDateDetailed(start_date) + " - " + formatDateDetailed(end_date);
    }
    MAX_DATE_RANGE = 14
    if(date_range > MAX_DATE_RANGE){
        date_range = MAX_DATE_RANGE;
    }
    end_date.setDate(start_date.getDate()+date_range-1);
    var timearea = document.createElement("div")
    timearea.setAttribute("style", "width: 100%; padding: 2px 6px 2px 6px;")
    // console.log("MIN END:", min_end, " VS end_date  ", end_date)
    if(date_range == 7 && start_date > min_start){
        var backarrow = document.createElement("span");
        backarrow.id = "backarrow";
        backarrow.className = "arrow";
        backarrow.innerText = "←";
        timearea.appendChild(backarrow);
    }
    var timedescription = document.createElement("span");
    timedescription.id = "timedescription";
    timedescription.setAttribute("style", "width: 220px; display: inline-block; text-align: center;")
    timedescription.innerText = timeDescriptionGet(start_date, end_date);
    timearea.appendChild(timedescription);
    if(date_range == MAX_DATE_RANGE && ((! min_end) || end_date < min_end)){
        var frontarrow = document.createElement("span");
        frontarrow.id = "frontarrow";
        frontarrow.innerText = "→";
        frontarrow.className = "arrow";
        timearea.appendChild(frontarrow);
    }



    parent.appendChild(timearea);
    parent.setAttribute("style", "min-width:" + 100 * date_range + "px;")
    function createCol(id){
        let colHolder = document.createElement("div");
        colHolder.setAttribute("class", "column")
        colHolder.setAttribute("style", "min-width: " + String(100/(date_range + 1)) + "%");
        colHolder.id = id;
        return colHolder;
    }
    function createHour(id){
        let hour = document.createElement("div");
        hour.id = id;
        hour.setAttribute("class", "hour")
        return hour;
    }
    function createDateLabel(time){
        var label = document.createElement("div");
        label.innerText= formatDate(time);
        label.setAttribute("class", "datelabel");
        return label;
    }
    function createTimeLabel(time){
        var label = document.createElement("div");
        if(time.getMinutes() == 0){
            label.innerText = formatTime(time);
        }
        
        label.setAttribute("class", "timelabel");
        return label;
    }
    function staticTimeColumn(){
        var col = createCol(-1)
        col.setAttribute("style", "max-width: 80px; margin-bottom: 9px;")
        var time = datetimeToDate(new Date());
        for(var hour = 0; hour < 48; hour++){
            var timelabel = createTimeLabel(time);
            time.setMinutes(time.getMinutes() + 30);
            col.appendChild(timelabel);
        }
        return col;
    }
    var current_date = new Date(+start_date)
    var id = 0;
    var firstCol = staticTimeColumn()
    parent.appendChild(firstCol);
    for(var day = 0; day < date_range; day++){
        var col = createCol(day);
        col.appendChild(createDateLabel(current_date));
       current_date.setDate(current_date.getDate()+1);
       
       parent.appendChild(col);
       for(var hour = 0; hour < 48; hour++){
           col.appendChild(createHour(id));
           id++;
       }

    }
}
