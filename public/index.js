let colours, slidr, opt1, opt2, opt3, rangeSlider, music, colourPicker, colourVal, bulb;
let disconModal = document.getElementById("disconModal");
let rangeValue = { current: 1.0, last: 1.0};

let manualLight = document.getElementById("manualLight");
let autoLED = document.getElementById("autoLED");
let musicMode = document.getElementById("musicMode");

function loadIn(){
    colours = document.getElementById("colours");
    slidr = document.getElementById("slidr");
    opt1 = document.getElementById("colourbutton");
    opt2 = document.getElementById("brightness");
    opt3 = document.getElementById("musicmode");

    bulb = document.getElementById("bulb")

    colourPicker = new iro.ColorPicker('#colours', {
        layout: [
            {
                component: iro.ui.Box,
                options: {
                    width: 100,
                    borderColor: '#ffffff',
                    colour: "#000000"
                }
            },
            {
                component: iro.ui.Slider,
                options: {
                    width: 100,
                    borderColor: '#000000',
                    sliderType: 'hue'
                }
            }
        ],
        layoutDirection: "vertical"
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

        document.getElementById("manualLight").disabled = true;
        document.getElementById("autoLED").disabled = true;
        document.getElementById("musicMode").disabled = true;

}

function enableRadioButtons(){
    document.getElementById("manualLight").disabled = false;
    document.getElementById("autoLED").disabled = false;
    document.getElementById("musicMode").disabled = false;
}

function updateChoice(){
    colours.style.visibility="hidden";
    slidr.style.visibility="hidden";
    music.style.visibility="hidden";

    if(document.getElementById("manualLight").checked){colours.style.visibility="visible"}
    if(document.getElementById("autoLED").checked){slidr.style.visibility="visible"}
    if(document.getElementById("musicMode").checked){music.style.visibility="visible"}
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

// Debugger function for Master Puru <3
function sendModeUpdate(flag) {
    let text;
    updateChoice();
    if (document.getElementById("manualLight").checked && flag === 0) {
        document.getElementById("autoLED").checked = false;
        document.getElementById("musicMode").checked = false;
        text = "100"
    } else if (document.getElementById("autoLED").checked && flag === 1) {
        document.getElementById("manualLight").checked = false;
        document.getElementById("musicMode").checked = false;
        text = "010"
    } else if (document.getElementById("musicMode").checked && flag === 2) {
       document.getElementById("manualLight").checked = false;
        document.getElementById("autoLED").checked = false;
        text = "001"
    } else if (!( document.getElementById("autoLED").checked || document.getElementById("manualLight").checked || document.getElementById("musicMode").checked)) {
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
    document.getElementById("manualLight").disabled = true;
    document.getElementById("autoLED").disabled = true;
    document.getElementById("musicMode").disabled = true;
    alert("You are now disconnected.");
}
