SEP = ","
TRUE = "1"


class LengthError(Exception):
    def __init__(self, arg=None):
        self.args = arg


class WrongValueReceived(Exception):
    def __init__(self, arg=None):
        self.args = arg


class InvalidTypeError(Exception):
    def __init__(self, arg=None):
        self.args = arg


class TooManyModesSelectedException(Exception):
    def __init__(self, arg=None):
        self.args = arg


def decodeString(code):
    """
    Decodes a string text
    :param code: the string code.
    :type code:str

    :return: the boolean values of the mode
    :rtype: bool, bool, bool
    """
    if len(code) != 3:
        raise LengthError(("Not a valid length Mode Code Received"))
    try:
        for char in code:
            if int(char) != 0 and int(char) != 1:
                raise WrongValueReceived(("Not a valid Mode Value"))
    except ValueError:
        raise InvalidTypeError("Can not accept non numeric characters")

    manualLED, autoLDR, musicMode = code[0] == TRUE, code[1] == TRUE, code[2] == TRUE
    modesSelected = manualLED + autoLDR + musicMode
    if modesSelected == 0 or modesSelected == 1:
        print(f"manualLED: {manualLED}, autoLDR: {autoLDR}, musicMode:{musicMode}")
        return manualLED, autoLDR, musicMode
    else:
        raise TooManyModesSelectedException(("Too many modes are selected can not turn them all on"))


def decodeColour(colour):
    """
    Decodes the colour string to a proper value and returns a tuple of the colour/
    :param colour: The colour String to decode
    :type colour: str
    :return: : Decoded tuple
    :rtype: tuple()
    """
    try:
        vals = colour.split(sep=SEP)
        if len(vals) != 3:
            raise LengthError("HEX String should only have 3 hexadecimal colours!")
        newColor = tuple(int(val) for val in vals)
        for hexValue in newColor:
            if 0 > hexValue or hexValue > 255:
                raise WrongValueReceived("Not a valid color Hex Value")
        print(f"New Colour: {colour}")
        return newColor
    except ValueError:
        raise InvalidTypeError("Can not accept non numeric characters")


def decodeBrightness(brightness):
    """
    Returns the decoded brightness from the string
    :param brightness: brightness in string format
    :return: :the float value of the brightness
    :rtype: float
    """
    try:
        value = float(brightness)
        if 0 <= value <= 1:
            print(f"Brightness: {brightness}")
            return value
        else:
            raise WrongValueReceived("Brightness can only be between 0 and 1")
    except ValueError:
        raise InvalidTypeError("Can not accept non numeric value")