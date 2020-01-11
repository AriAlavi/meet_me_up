function stripDateDetails(givenDate){

}
CACHE = {}
function getData(url, attribute){
    Object.keys(CACHE).forEach(function(key){
        if(key == attribute){
            return CACHE[key]; //key is a string, so could the problem be that we were indexing using a string???
        }
        return $.get(url, function(data){
            return JSON.parse(data);
        })
    })
}