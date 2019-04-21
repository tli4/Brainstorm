var i = 100;

var counterBack = setInterval(function(){
  i--;
  if (i > 0){
    $('.progress-bar').css('width', i+'%');
  } else {
    clearInterval(counterBack);
  }
  
}, 1000);

var selected = "";

function submit() {
    console.log(1);
    if (selected == answer){
        document.location.href = '/correct';
    } else {
        document.location.href = '/wrong';
    }
}

function select(str) {
    selected = str;
}

function next() {
    document.location.href = '/index';
}

$("#searchbar").keyup(function(event) {
    if (event.keyCode === 13) {
        $("#myButton").click();
    }
});

function back() {
    history.go(-1);
}