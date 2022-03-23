function LTrim(str){
    var i;
    for(i=0;i<str.length;i++){
        if(str.charAt(i)!=" ")
            break;
    }
    str = str.substring(i,str.length);
    return str;
}

function RTrim(str){
    var i;
    for(i=str.length-1;i>=0;i--){
        if(str.charAt(i)!=" ")
            break;
    }
    str = str.substring(0,i+1);
    return str;
}

function IsEmpty(str){
    str = LTrim(str);
    str = RTrim(str);
    return str == "";
}

function httpPost(URL, PARAMS) {
    var temp = document.createElement("form");
    temp.action = URL;
    temp.method = "post";
    temp.style.display = "none";

    for (var x in PARAMS) {
        var opt = document.createElement("textarea");
        opt.name = x;
        opt.value = PARAMS[x];
        temp.appendChild(opt);
 }
    document.body.appendChild(temp);
    temp.submit();
    return temp;
}

function httpJson(url){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function(){
        if(xhr.readyState == 4){
            eval("var success=" + xhr.responseText);
            return success;
        }
    }
    xhr.open("get", url);
    xhr.send(null);
}