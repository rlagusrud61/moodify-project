let colours, slidr, opt1, opt2, opt3, rangeSlider, manualLight, autoLDR, musicMode, music, colourPicker, colourVal, bulb;
let disconModal = document.getElementById("disconModal");
let rangeValue = { current: 1.0, last: 1.0};

window.onload = compatibilityCtr();

function compatibilityCtr(){
    var nAgt = navigator.userAgent;
    var browserName  = navigator.appName;
    var fullVersion  = ''+parseFloat(navigator.appVersion); 
    var majorVersion = parseInt(navigator.appVersion,10);
    var navUsAg = window.navigator.userAgent;

    var OSName = "Unknown";
    if (navUsAg.indexOf("Windows NT 10.0")!= -1) {OSName="Windows 10";}
    else if (navUsAg.indexOf("Windows NT 6.2") != -1) {OSName="Windows 8";}
    else if (navUsAg.indexOf("Windows NT 6.1") != -1) OSName="Windows 7";
    else if (navUsAg.indexOf("Windows NT 6.0") != -1) OSName="Windows Vista";
    else if (navUsAg.indexOf("Windows NT 5.1") != -1) OSName="Windows XP";
    else if (navUsAg.indexOf("Windows NT 5.0") != -1) OSName="Windows 2000";
    else if (navUsAg.indexOf("Mac")            != -1) OSName="Mac/iOS";
    else if (navUsAg.indexOf("X11")            != -1) OSName="UNIX";
    else if (navUsAg.indexOf("Linux")          != -1) OSName="Linux";


    // In Opera, the true version is after "Opera" or after "Version"
    if ((verOffset=nAgt.indexOf("Opera"))!=-1) {
    browserName = "Opera";
    fullVersion = nAgt.substring(verOffset+6);
    if ((verOffset=nAgt.indexOf("Version"))!=-1) 
    fullVersion = nAgt.substring(verOffset+8);
    }
    // In MSIE, the true version is after "MSIE" in userAgent
    else if ((verOffset=nAgt.indexOf("MSIE"))!=-1) {
    browserName = "MSIE";
    }
    // In Chrome, the true version is after "Chrome" 
    else if ((verOffset=nAgt.indexOf("Chrome"))!=-1) {
    browserName = "Chrome";
    fullVersion = nAgt.substring(verOffset+7);
    }
    // In Safari, the true version is after "Safari" or after "Version" 
    else if ((verOffset=nAgt.indexOf("Safari"))!=-1) {
    browserName = "Safari";
    }
    // In Firefox, the true version is after "Firefox" 
    else if ((verOffset=nAgt.indexOf("Firefox"))!=-1) {
    browserName = "Firefox";
    }
    // In most other browsers, "name/version" is at the end of userAgent 
    else if ( (nameOffset=nAgt.lastIndexOf(' ')+1) < 
            (verOffset=nAgt.lastIndexOf('/')) ) 
    {
    browserName = nAgt.substring(nameOffset,verOffset);
    fullVersion = nAgt.substring(verOffset+1);
    }
    // trim the fullVersion string at semicolon/space if present
    if ((ix=fullVersion.indexOf(";"))!=-1)
    fullVersion=fullVersion.substring(0,ix);
    if ((ix=fullVersion.indexOf(" "))!=-1)
    fullVersion=fullVersion.substring(0,ix);

    majorVersion = parseInt(''+fullVersion,10);
    if (isNaN(majorVersion)) {
    fullVersion  = ''+parseFloat(navigator.appVersion); 
    majorVersion = parseInt(navigator.appVersion,10);
    }

    if(browserName == "Firefox"){
        alert("This browser is not supported by our product");
    } else if(browserName == "Safari"){
        alert("This browser is not supported by our product");
    } else if(browserName == "MSIE"){
        alert("This browser is not supported by our product");
    } else if(browserName == "Chrome" && (majorVersion < 56 || (majorVersion < 70 && OSName == "Windows 10"))){
        alert("Please update Google Chrome");
    } else if(browserName == "Edge" && majorVersion > 79){
        alert("The new version of Edge are not compatible, use version 79 or lower");}
    else if (browserName == "Opera" && (majorVersion < 43 || (majorVersion < 57 && OSName == "Windows 10") )){
        alert("Please update Opera");}
    }


function loadIn(){
    colours = document.getElementById("colours");
    slidr = document.getElementById("slidr");
    opt1 = document.getElementById("contactChoice1");
    opt2 = document.getElementById("contactChoice2");
    opt3 = document.getElementById("contactChoice3");

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
    bulb.style.background = color.hexString
    bulb.style.boxShadow = `0px 0px 15px 0px ${color.hexString}`
    sendColourUpdate(stringCode);
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
function sendModeUpdate(flag) {
    let text;
    if (manualLight.checked && flag === 0) {
        autoLDR.checked = false;
        musicMode.checked = false;
        text = "100"
    } else if (autoLDR.checked && flag === 1) {
        manualLight.checked = false;
        musicMode.checked = false;
        text = "010"
    } else if (musicMode.checked && flag === 2) {
        manualLight.checked = false;
        autoLDR.checked = false;
        text = "001"
    } else if (!(autoLDR.checked || manualLight.checked || musicMode.checked)) {
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
