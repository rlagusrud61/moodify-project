import unittest
from MoodifyDriver \
    import TooManyModesSelectedException, InvalidTypeError, WrongValueReceived, LengthError, \
    decodeString, decodeBrightness, decodeColour

class TestStringMethods(unittest.TestCase):
    
    def test_decodeStringAllValid(self):
        value1, value2, value3 = decodeString("000")
        self.assertFalse(value1)
        self.assertFalse(value2)
        self.assertFalse(value3)

        value1, value2, value3 = decodeString("001")
        self.assertFalse(value1)
        self.assertFalse(value2)
        self.assertTrue(value3)

        value1, value2, value3 = decodeString("010")
        self.assertFalse(value1)
        self.assertTrue(value2)
        self.assertFalse(value3)

        value1, value2, value3 = decodeString("100")
        self.assertTrue(value1)
        self.assertFalse(value2)
        self.assertFalse(value3)
    
    def test_decodeStringIllegalCharacters(self):
        with self.assertRaises(InvalidTypeError):
            value1, value2, value3 = decodeString("a00")
        with self.assertRaises(InvalidTypeError):
            value1, value2, value3 = decodeString("0a0")
        with self.assertRaises(InvalidTypeError):
            value1, value2, value3 = decodeString("00a")
        with self.assertRaises(InvalidTypeError):
            value1, value2, value3 = decodeString("aaa")
    
    def test_decodeStringIllegalCharactersWithLegalModeSelect(self):
        with self.assertRaises(InvalidTypeError):
            value1, value2, value3 = decodeString("a10")
        with self.assertRaises(InvalidTypeError):
            value1, value2, value3 = decodeString("0a1")
        with self.assertRaises(InvalidTypeError):
            value1, value2, value3 = decodeString("10a")

    def test_TooManyModesSelected(self):
        with self.assertRaises(TooManyModesSelectedException):
            value1, value2, value3 = decodeString("110")
        with self.assertRaises(TooManyModesSelectedException):
            value1, value2, value3 = decodeString("011")
        with self.assertRaises(TooManyModesSelectedException):
            value1, value2, value3 = decodeString("111")
        with self.assertRaises(TooManyModesSelectedException):
            value1, value2, value3 = decodeString("101")
    
    def test_wrongStringFormat(self):
        with self.assertRaises(LengthError):
            value1, value2, value3 = decodeString("1000")
        with self.assertRaises(LengthError):
            value1, value2, value3 = decodeString("10")
    
    def test_wrongNumbersUsed(self):
        with self.assertRaises(WrongValueReceived):
            value1, value2, value3 = decodeString("200")
        with self.assertRaises(WrongValueReceived):
            value1, value2, value3 = decodeString("108")

    def test_validColour(self):
        self.assertEqual(decodeColour("122,133,144"), (122,133,144))
        self.assertEqual(decodeColour("0,0,0"), (0,0,0))
    
    def test_invalidColour(self):
        with self.assertRaises(WrongValueReceived):
            newColour = decodeColour("256,0,0")
        with self.assertRaises(WrongValueReceived):
            newColour = decodeColour("0,-1,0")
        with self.assertRaises(WrongValueReceived):
            newColour = decodeColour("0,0,9000")
    
    def test_moreLessHexValuesThanNeeded(self):
        with self.assertRaises(LengthError):
            newColour = decodeColour("250,0,0,0")
        with self.assertRaises(LengthError):
            newColour = decodeColour("250,0")
    
    def test_invalidChars(self):
        with self.assertRaises(InvalidTypeError):
            newColour = decodeColour("25-,0,0")
        with self.assertRaises(InvalidTypeError):
            newColour = decodeColour("2a6,0,0")
        with self.assertRaises(InvalidTypeError):
            newColour = decodeColour("256,err,or")
    
    def test_brightnessValid(self):
        self.assertEqual(decodeBrightness("0.132435"), 0.132435)
        self.assertEqual(decodeBrightness("1.0000"), 1.0)
        self.assertEqual(decodeBrightness("000000"), 0)
    
    def test_invalidBrightnessValue(self):
        with self.assertRaises(WrongValueReceived):
            brightness = decodeBrightness("2")
        with self.assertRaises(WrongValueReceived):
            brightness = decodeBrightness("-1")
    
    def test_invalidBrightnessChars(self):
        with self.assertRaises(InvalidTypeError):
            brightness = decodeBrightness("256,err,or")
        with self.assertRaises(InvalidTypeError):
            brightness = decodeBrightness("0.00--fd")
        with self.assertRaises(InvalidTypeError):
            brightness = decodeBrightness("0.749g5")

if __name__ == '__main__':
    unittest.main()