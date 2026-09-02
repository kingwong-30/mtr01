import Toybox.Graphics;
import Toybox.Lang;

// All positions are fractions of the current screen size, plus real font
// metrics from the device. Never hardcode pixels: FR165 is 390x390,
// FR970 is 454x454, and both share this layout.
class FaceLayout {

    var w as Number = 0;
    var h as Number = 0;
    var cx as Number = 0;
    var cy as Number = 0;

    var dateY as Number = 0;
    var timeY as Number = 0;
    var secondsY as Number = 0;
    var statsY as Number = 0;
    var statsLabelY as Number = 0;

    var leftX as Number = 0;
    var rightX as Number = 0;

    var frameRadius as Number = 0;
    var frameRadiusInner as Number = 0;
    var frameStroke as Number = 2;
    var frameStrokeSleep as Number = 1;
    var frameStrokeInner as Number = 1;
    var tickOuter as Number = 0;
    var tickInner as Number = 0;
    var tickMajorInner as Number = 0;

    var timeFont as Graphics.FontDefinition = Graphics.FONT_NUMBER_HOT;
    var secondsFont as Graphics.FontDefinition = Graphics.FONT_SMALL;
    var dateFont as Graphics.FontDefinition = Graphics.FONT_TINY;
    var statsFont as Graphics.FontDefinition = Graphics.FONT_SMALL;
    var statsLabelFont as Graphics.FontDefinition = Graphics.FONT_XTINY;

    var shiftX as Number = 0;
    var shiftY as Number = 0;

    function initialize() {
    }

    function compute(dc as Dc) as Void {
        w = dc.getWidth();
        h = dc.getHeight();
        cx = w / 2;
        cy = h / 2;

        // System fonts already scale with the device. Pick a smaller
        // number font only on compact round screens (~360px).
        if (w < 380) {
            timeFont = Graphics.FONT_NUMBER_MEDIUM;
            statsFont = Graphics.FONT_TINY;
        } else {
            timeFont = Graphics.FONT_NUMBER_HOT;
            statsFont = Graphics.FONT_SMALL;
        }

        var timeHeight = dc.getFontHeight(timeFont);
        var dateHeight = dc.getFontHeight(dateFont);
        var statsHeight = dc.getFontHeight(statsFont);
        var gap = (h * 0.02).toNumber();
        if (gap < 4) {
            gap = 4;
        }

        timeY = (cy - (h * 0.04)).toNumber();
        dateY = timeY - (timeHeight / 2) - dateHeight - gap;
        secondsY = timeY + (timeHeight / 2) + (h * 0.008).toNumber();
        statsY = (cy + (h * 0.28)).toNumber();
        statsLabelY = statsY + statsHeight + 1;

        leftX = (w * 0.25).toNumber();
        rightX = (w * 0.75).toNumber();

        frameStroke = (w * 0.012).toNumber();
        if (frameStroke < 2) {
            frameStroke = 2;
        }
        frameStrokeSleep = frameStroke / 2;
        if (frameStrokeSleep < 1) {
            frameStrokeSleep = 1;
        }
        frameStrokeInner = frameStroke - 1;
        if (frameStrokeInner < 1) {
            frameStrokeInner = 1;
        }

        frameRadius = cx - frameStroke - 1;
        frameRadiusInner = (frameRadius * 0.92).toNumber();
        tickOuter = frameRadius - 1;
        tickInner = (tickOuter - (w * 0.035)).toNumber();
        tickMajorInner = (tickOuter - (w * 0.055)).toNumber();

        shiftX = 0;
        shiftY = 0;
    }

    // AMOLED burn-in: nudge the whole face by 1px while sleeping.
    function applyBurnInShift(sleeping as Boolean, minute as Number) as Void {
        if (!sleeping) {
            shiftX = 0;
            shiftY = 0;
            return;
        }
        shiftX = (minute % 3) - 1;
        shiftY = ((minute / 3) % 3) - 1;
    }

    function ox() as Number {
        return cx + shiftX;
    }

    function oy() as Number {
        return cy + shiftY;
    }
}
