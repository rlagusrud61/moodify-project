let colours;
let slidr;
let opt1;
let opt2;
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

    if(opt1.checked===true){colours.style.visibility="visible"}
    if(opt2.checked===true){slidr.style.visibility="visible"}
    /*else{}*/
}



let span = document.getElementsByClassName("close")[0];

function modalPopUp() {disconModal.style.display = "block";}

function closing(){disconModal.style.display = "none";}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target === disconModal) {
        modal.style.display = "none";
    }
}

// Debugger function for Master Puru <3
function sendUpdate(pressed) {
    let manualLight = document.getElementById("ManualLight");
    let autoLDR = document.getElementById("LightIntensityMode");
    let text;
    if (manualLight.checked === true && pressed === 0) {
        autoLDR.checked = false;
        text = "110"

    } else if (autoLDR.checked === true) {
        manualLight.checked = false;
        text = "001"
    } else if (autoLDR.checked === false && manualLight.checked === false) {
        text = "000"
    }
    writeVal(text)
    console.log(text)
}

function disconnect(){
    bleDisconnect()
    alert("You are now disconnected. Bai!");
}
