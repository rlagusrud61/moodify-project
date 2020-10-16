var colours;
var slidr;
var opt1;
var opt2;
let disconModal = document.getElementById("disconModal");

function loadIn(){
    colours = document.getElementById("colours");
    slidr = document.getElementById("slidr");
    opt1 = document.getElementById("contactChoice1");
    opt2 = document.getElementById("contactChoice2");
}


function updateChoice(){
    colours.style.visibility="hidden";
    slidr.style.visibility="hidden";
    
    if(opt1.checked==true){colours.style.visibility="visible"}
    if(opt2.checked==true){slidr.style.visibility="visible"}
    /*else{}*/
}



var span = document.getElementsByClassName("close")[0];

function modalPopUp() {disconModal.style.display = "block";}

function closing(){disconModal.style.display = "none";}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == disconModal) {
    modal.style.display = "none";
  }
} 

// Debugger function for Master Puru <3
function debug() {
  let toggle = document.getElementById("toggle_btn");

  if (toggle.checked == true) {
    console.log("Baaaaby I'm ON!");
  } else {
    console.log("I'm off. Bai");
  }
}

function disconnect(){
  alert("You are now disconnected. Bai!");
}
