function stripDateDetails(givenDate){

}
CACHE = {}
function getData(url, attribute){
    Object.keys(CACHE).forEach(function(key){
        if(key == attribute){
            return CACHE[key];
        }
        return $.get(url, function(data){
            return JSON.parse(data);
        })
    })
}