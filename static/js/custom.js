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
    document.location.href = '/game';
}