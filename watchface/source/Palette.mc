import Toybox.Application;
import Toybox.Lang;

class Palette {

    var frameStyle as Number = 0;
    var frameColor as Number = 0x2EC4B6;
    var textColor as Number = 0xF2F4F7;
    var mutedColor as Number = 0x8B9098;
    var accentColor as Number = 0x2EC4B6;

    function initialize() {
    }

    function load(sleeping as Boolean) as Void {
        frameStyle = readNumber("FrameStyle", 0);
        var colorId = readNumber("FrameColor", 3);

        frameColor = colorFor(colorId, sleeping);
        accentColor = frameColor;
        if (sleeping) {
            textColor = 0x9AA0A6;
            mutedColor = 0x5C6168;
        } else {
            textColor = 0xF2F4F7;
            mutedColor = 0x8B9098;
        }
    }

    function readNumber(key as String, fallback as Number) as Number {
        var value = Application.Properties.getValue(key);
        if (value instanceof Number) {
            return value as Number;
        }
        return fallback;
    }

    function colorFor(id as Number, sleeping as Boolean) as Number {
        if (sleeping) {
            if (id == 0) { return 0x4A4C4F; }
            if (id == 1) { return 0x6B5614; }
            if (id == 2) { return 0x6E7276; }
            if (id == 3) { return 0x1A6E67; }
            if (id == 4) { return 0x8A3D36; }
            if (id == 5) { return 0x33408A; }
            return 0x1A6E67;
        }
        if (id == 0) { return 0x8A8D91; }
        if (id == 1) { return 0xC9A227; }
        if (id == 2) { return 0xC0C4C8; }
        if (id == 3) { return 0x2EC4B6; }
        if (id == 4) { return 0xFF6F61; }
        if (id == 5) { return 0x5B6CFF; }
        return 0x2EC4B6;
    }
}
