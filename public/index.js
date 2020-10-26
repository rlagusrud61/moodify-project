let colours, slidr, opt1, opt2, opt3, rangeSlider, manualLight, autoLDR, musicMode, music, colourPicker, colourVal, bulb;
let disconModal = document.getElementById("disconModal");
let rangeValue = { current: 1.0, last: 1.0};

function loadIn(){
    colours = document.getElementById("colours");
    slidr = document.getElementById("slidr");
    opt1 = document.getElementById("manual");
    opt2 = document.getElementById("mood");
    opt3 = document.getElementById("music");

    bulb = document.getElementById("bulb")

    manualLight = document.getElementById("ManualLight");
    autoLDR = document.getElementById("LightIntensityMode");
    musicMode = document.getElementById("MusicMode");

    colourPicker = new iro.ColorPicker('#colours', {
        layout: [
            {
                component: iro.ui.Box,
                options: {
                    width: 75,
                    borderColor: '#ffffff',
                    colour: "#000000"
                }
            },
            {
                component: iro.ui.Slider,
                options: {
                    width: 75,
                    borderColor: '#000000',
                    sliderType: 'hue'
                }
            }
        ],
        layoutDirection: "horizontal"
    });
    colourVal = colourPicker.color.hexString;

    music = document.getElementById("musicToggle")

    rangeSlider = document.getElementById("range_slider");
    // rangeSlider.addEventListener("mousedown", function() {
    //     rangeSlider.addEventListener("mousemove", brightnessListener);
    // });

    rangeSlider.addEventListener("mouseup", function () {
        // rangeSlider.removeEventListener("mousemove", brightnessListener)
        brightnessListener()
    });

    colourPicker.on('color:change', onColorChange);

    updateChoice();

    opt1.disabled = true;
    opt2.disabled = true;
    opt3.disabled = true;

}


function updateChoice(){
    colours.style.visibility="hidden";
    slidr.style.visibility="hidden";
    music.style.visibility="hidden";

    if(opt1.checked){colours.style.visibility="visible"}
    if(opt2.checked){slidr.style.visibility="visible"}
    if(opt3.checked){music.style.visibility="visible"}
    /*else{}*/
}

function onColorChange(color) {
    ({r, g, b} = color.rgb);
    let stringCode = `${r},${g},${b}`;
    // console.log(stringCode);
    bulb.style.background = color.hexString
    bulb.style.boxShadow = `0px 0px 15px 0px ${color.hexString}`
    sendColourUpdate(stringCode);
}

let span = document.getElementsByClassName("close")[0];

function modalPopUp() {disconModal.style.display = "block";}

function closing(){disconModal.style.display = "none";}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target === disconModal){modal.style.display = "none";}
}

function changeState(flag){
    updateChoice();
    sendModeUpdate(flag);
}

// Debugger function for Master Puru <3
function sendModeUpdate(flag) {
    let text;
    if (opt1.checked && flag === 0) {
        opt2.checked = false;
        opt3.checked = false;
        text = "100"
    } else if (opt2.checked && flag === 1) {
        opt1.checked = false;
        opt3.checked = false;
        text = "010"
    } else if (opt3.checked && flag === 2) {
        opt1.checked = false;
        opt2.checked = false;
        text = "001"
    } else if (!(opt1.checked || opt2.checked || opt3.checked)) {
        text = "000"
    }
    console.log({mode: text})
    writeVal(text)
}

function sendColourUpdate(colourString) {
    // the format of the colour should be int,int,int,
    // so each color value separated by a comma and nothing else, no floats
    writeColour(colourString)
}

let brightnessListener = function() {
    rangeValue.current = rangeSlider.value;
    if (rangeValue.current !== rangeValue.last) {
        rangeValue.last = rangeValue.current;
        writeBrightness(rangeValue.current);
    }
};

function disconnect(){
    bleDisconnect()
    alert("You are now disconnected. Bai!");
}
