on_array = {}

function turn_on(button) {
    key = button.id
    if (key in on_array) {
        if(on_array[key]){
            on_array[key] = false
        }else{
            on_array[key] = true
        }
    } else {
        on_array[key] = false
    }

    if(on_array[key] == false){
        var elements = document.getElementsByClassName(key);
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            element.hidden = true;
        }
    }else{
        var elements = document.getElementsByClassName(key);
        for (var i = 0; i < elements.length; i++) {
            var element = elements[i];
            element.hidden = false;
        }
    }
}