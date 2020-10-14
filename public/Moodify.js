var colours;
var slidr;
var opt1;
var opt2

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

function modalPopUp() {document.getElementById("disconModal").style.display = "block";}

function closing(){document.getElementById("myModal").style.display = "none";}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
} 
