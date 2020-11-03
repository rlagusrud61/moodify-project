let colours, slidr, opt1, opt2, opt3, rangeSlider, music, colourPicker, colourVal, bulb;
let disconModal = document.getElementById("disconModal");
let rangeValue = { current: 1.0, last: 1.0};

let manualLight = document.getElementById("manualLight");
let autoLED = document.getElementById("autoLED");
let musicMode = document.getElementById("musicMode");

let currentMode= "000";

/**
 This method is called whenever index.html is loaded. A colour picker is created. All the switches and
 radio buttons are disabled, as the web interface is not connected to the Pi yet.
*/
function loadIn(){
    compatibilityCtr();
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
                    width: 150,
                    borderColor: '#ffffff',
                    colour: "#000000"
                }
            },
            {
                component: iro.ui.Slider,
                options: {
                    width: 150,
                    borderColor: '#000000',
                    sliderType: 'hue'
                }
            }
        ],
        layoutDirection: "vertical"
    });
    colourVal = colourPicker.color.hexString;

    rangeSlider = document.getElementById("range_slider");


    rangeSlider.addEventListener("mouseup", function () {
        brightnessListener()
    });

    colourPicker.on('color:change', onColorChange);

    updateChoice();

    document.getElementById("manualLight").disabled = true;
    document.getElementById("autoLED").disabled = true;
    document.getElementById("musicMode").disabled = true;
    document.getElementById("lightSwitch").disabled = true;
}

/**
    This method is used by the switch in the sidebar to turn on and off the lights when the web interface
    is connected to the Pi via Bluetooth.
*/
async function lightOff(){
    if (!document.getElementById("lightSwitch").checked){
        await writeVal("000"); // turns manual LED on and
    } else {
        await writeVal(currentMode);
    }
}

/**
    This method is used to enable the switches and radio buttons once the web interface is connected to the
    Pi via Bluetooth.
*/
function enableRadioButtons(){
    document.getElementById("manualLight").disabled = false;
    document.getElementById("autoLED").disabled = false;
    document.getElementById("musicMode").disabled = false;
    document.getElementById("lightSwitch").disabled = false;
    document.getElementById("lightSwitch").checked = true;
}

/**
    This method is used to display the slider, colour picker and light bulb to correspond to one of the three
    modes which was chosen.
*/
function updateChoice(){
    colours.style.visibility="hidden";
    slidr.style.visibility="hidden";

    let bulb = document.getElementById("bulb");
    if(document.getElementById("manualLight").checked){colours.style.visibility="visible"; slidr.style.visibility="visible"; colours.style.left=null; colours.style.position=null; bulb.innerHTML="";}
    if(document.getElementById("autoLED").checked){colours.style.visibility="visible";colours.style.left="150px"; colours.style.position="relative"; bulb.innerHTML="";}
    if (document.getElementById("musicMode").checked){bulb.innerHTML = "<img src='https://imgur.com/kgXlCfr.gif' alt='Disco woo' style='width=150'/>"}
}

/**
    It detects the colour change from the colour picker, alters the colour of the light bulb and then sends
    this update to the Raspberry Pi via Bluetooth.
*/
function onColorChange(color) {
    ({r, g, b} = color.rgb);
    let stringCode = `${r},${g},${b}`;
    // console.log(stringCode);
    bulb.style.background = color.hexString
    bulb.style.boxShadow = `0px 0px 15px 0px ${color.hexString}`
    sendColourUpdate(stringCode);
}

/**
    It detects the mode change from the radio buttons, displays the corresponding changes in the web
    interface and then sends this update to the Raspberry Pi via Bluetooth.
*/
function sendModeUpdate(flag) {
    let text;
    updateChoice();
    document.getElementById("lightSwitch").checked=true;
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
    currentMode = text;
    writeVal(text)
}

/**
    This method is used to send the colour change on the colour picker to the Raspberry Pi via Bluetooth.
*/
function sendColourUpdate(colourString) {
    // the format of the colour should be int,int,int,
    // so each color value separated by a comma and nothing else, no floats
    writeColour(colourString)
}

/**
    This method detects the changes in the slider which correspond to the brightness of the light and sends
    this signal to the Raspberry Pi via Bluetooth.
*/
let brightnessListener = function() {
    rangeValue.current = rangeSlider.value;
    if (rangeValue.current !== rangeValue.last) {
        rangeValue.last = rangeValue.current;
        writeBrightness(rangeValue.current);
    }
};

/**
    This method is called when the user clicks on the Disconnect button on the sidebar. This method disables all
    the switches and radio buttons and hides the slider and colour picker. It also displays an alert message
    to the user to indicate that the web interface is no longer connected to the Raspberry Pi via Bluetooth.
*/
function disconnect(){
    bleDisconnect()
    document.getElementById("manualLight").disabled = true;
    document.getElementById("autoLED").disabled = true;
    document.getElementById("musicMode").disabled = true;
    document.getElementById("lightSwitch").checked = false;
    document.getElementById("lightSwitch").disabled = true;
    colours.style.visibility="hidden";
    slidr.style.visibility="hidden";
    music.style.visibility="hidden";
    document.getElementById("bulb").style.backgroundColor = "rgba(39, 38, 38, 0.342)";
    document.getElementById("bulb").style.boxShadow = "0 0 15px 0 black";
    alert("You are now disconnected.");
}

/**
 * This function checks if the browser is compatible with the Web Bluetooth API. 
 * It searches for the browser, the version of the browser and the operating system of the device. 
 * It then checks whether the browser is compatible, or if this version of the browser is compatible on the OS of the device. 
 * If it if not compatible, the user gets an alert box that shows whether they should use another browser, or if they should update/downgrade they browser. 
 */
function compatibilityCtr(){
    var nAgt = navigator.userAgent;  // This contains information about the browser
    var browserName  = navigator.appName;  // This contains the browser name
    var fullV  = ''+parseFloat(navigator.appVersion);  // This contains the full version of the browser
    var majorV = parseInt(navigator.appVersion,10);  // This contains the major version of the browser
    var navUsAg = window.navigator.userAgent;  // This contains the Operating System of the device

    // navUsAg contains the name of the OS, so it searches for the true OS
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
    fullV = nAgt.substring(verOffset+6);
    if ((verOffset=nAgt.indexOf("Version"))!=-1)
    fullV = nAgt.substring(verOffset+8);
    }
    // In MSIE, the true version is after "MSIE" in userAgent
    else if ((verOffset=nAgt.indexOf("MSIE"))!=-1) {
    browserName = "MSIE";
    }
    // In Chrome, the true version is after "Chrome"
    else if ((verOffset=nAgt.indexOf("Chrome"))!=-1) {
    browserName = "Chrome";
    fullV = nAgt.substring(verOffset+7);
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
    fullV = nAgt.substring(verOffset+1);
    }
    // trim the fullV string at semicolon/space if present
    if ((ix=fullV.indexOf(";"))!=-1)
    fullV=fullV.substring(0,ix);
    if ((ix=fullV.indexOf(" "))!=-1)
    fullV=fullV.substring(0,ix);

    majorV = parseInt(''+fullV,10);
    if (isNaN(majorV)) {
    fullV  = ''+parseFloat(navigator.appVersion);
    majorV = parseInt(navigator.appVersion,10);
    }

    // Checks for compatibility and makes the alert box
    if(browserName == "Firefox"){
        alert("The web interface for Moodify does not support this browser.");
    } else if(browserName == "Safari"){
        alert("The web interface for Moodify does not support this browser.");
    } else if(browserName == "MSIE"){
        alert("The web interface for Moodify does not support this browser.");
    } else if(browserName == "Chrome" && (majorV < 56 || (majorV < 70 && OSName == "Windows 10"))){
        alert("Please update Google Chrome.");
    } else if(browserName == "Edge" && majorV > 79){
        alert("The newer versions of Edge are not compatible. Please use version 79 or lower.");}
    else if (browserName == "Opera" && (majorV < 43 || (majorV < 57 && OSName == "Windows 10") )){
        alert("Please update Opera.");}
}
