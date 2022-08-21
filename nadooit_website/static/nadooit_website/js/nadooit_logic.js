var node = document.getElementsByClassName("portal")[0];
var node2 = document.getElementsByClassName("portal")[1];
var longpress = false;
var presstimer = null;
var longtarget = null;

var cancel = function(e) {
    if (presstimer !== null) {
        clearTimeout(presstimer);
        presstimer = null;
    }
    
    this.classList.remove("longpress");
};

var click = function(e) {
    if (presstimer !== null) {
        clearTimeout(presstimer);
        presstimer = null;
    }
    
    this.classList.remove("longpress");
    
    if (longpress) {
        return false;
    }
    
};

var start = function(e) {
    console.log(e);
    
    if (e.type === "click" && e.button !== 0) {
        return;
    }
    
    longpress = false;
    
    this.classList.add("longpress");
    
    presstimer = setTimeout(function() {
        //redirect to /admin/ route of the current website
        window.location.href = "/admin/";   
        longpress = true;
    }, 1000);
    
    return false;
};

node.addEventListener("mousedown", start);
node.addEventListener("touchstart", start);
node.addEventListener("click", click);
node.addEventListener("mouseout", cancel);
node.addEventListener("touchend", cancel);
node.addEventListener("touchleave", cancel);
node.addEventListener("touchcancel", cancel);
node2.addEventListener("mousedown", start);
node2.addEventListener("touchstart", start);
node2.addEventListener("click", click);
node2.addEventListener("mouseout", cancel);
node2.addEventListener("touchend", cancel);
node2.addEventListener("touchleave", cancel);
node2.addEventListener("touchcancel", cancel);