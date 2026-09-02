import Toybox.Application;
import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Math;
import Toybox.WatchUi;

class KlarView extends WatchUi.WatchFace {

    private var _layout as FaceLayout;
    private var _palette as Palette;
    private var _data as FaceData;
    private var _sleeping as Boolean;
    private var _labelHr as String;
    private var _labelSteps as String;
    private var _labelBattery as String;

    function initialize() {
        WatchFace.initialize();
        _layout = new FaceLayout();
        _palette = new Palette();
        _data = new FaceData();
        _sleeping = false;
        _labelHr = "HR";
        _labelSteps = "STEPS";
        _labelBattery = "BAT";
    }

    function onLayout(dc as Dc) as Void {
        _layout.compute(dc);
        _labelHr = Application.loadResource(Rez.Strings.LabelHr) as String;
        _labelSteps = Application.loadResource(Rez.Strings.LabelSteps) as String;
        _labelBattery = Application.loadResource(Rez.Strings.LabelBattery) as String;
    }

    function onShow() as Void {
    }

    function onHide() as Void {
    }

    function onExitSleep() as Void {
        _sleeping = false;
        WatchUi.requestUpdate();
    }

    function onEnterSleep() as Void {
        _sleeping = true;
        WatchUi.requestUpdate();
    }

    function onUpdate(dc as Dc) as Void {
        if (dc has :setAntiAlias) {
            dc.setAntiAlias(true);
        }

        _data.refresh();
        _palette.load(_sleeping);
        _layout.applyBurnInShift(_sleeping, _data.minute);

        dc.setColor(Graphics.COLOR_BLACK, Graphics.COLOR_BLACK);
        dc.clear();

        drawFrame(dc);
        drawDate(dc);
        drawTime(dc);
        drawStats(dc);
    }

    function drawFrame(dc as Dc) as Void {
        var cx = _layout.ox();
        var cy = _layout.oy();
        var stroke = _sleeping ? _layout.frameStrokeSleep : _layout.frameStroke;

        dc.setColor(_palette.frameColor, Graphics.COLOR_TRANSPARENT);
        dc.setPenWidth(stroke);
        dc.drawCircle(cx, cy, _layout.frameRadius);

        if (_palette.frameStyle == 1) {
            dc.setPenWidth(_sleeping ? 1 : _layout.frameStrokeInner);
            dc.drawCircle(cx, cy, _layout.frameRadiusInner);
        } else if (_palette.frameStyle == 2) {
            drawTicks(dc, cx, cy);
        }
    }

    function drawTicks(dc as Dc, cx as Number, cy as Number) as Void {
        for (var i = 0; i < 12; i += 1) {
            var isMajor = (i % 3) == 0;
            if (!_sleeping || isMajor) {
                var inner = isMajor ? _layout.tickMajorInner : _layout.tickInner;
                var width = isMajor ? (_sleeping ? 1 : 2) : 1;
                var angle = Math.toRadians((i * 30) - 90);
                var cos = Math.cos(angle);
                var sin = Math.sin(angle);

                var x1 = (cx + inner * cos).toNumber();
                var y1 = (cy + inner * sin).toNumber();
                var x2 = (cx + _layout.tickOuter * cos).toNumber();
                var y2 = (cy + _layout.tickOuter * sin).toNumber();

                dc.setPenWidth(width);
                dc.drawLine(x1, y1, x2, y2);
            }
        }
    }

    function drawDate(dc as Dc) as Void {
        dc.setColor(_palette.mutedColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(
            _layout.ox(),
            _layout.dateY + _layout.shiftY,
            _layout.dateFont,
            _data.dateText,
            Graphics.TEXT_JUSTIFY_CENTER
        );
    }

    function drawTime(dc as Dc) as Void {
        dc.setColor(_palette.textColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(
            _layout.ox(),
            _layout.timeY + _layout.shiftY,
            _layout.timeFont,
            _data.timeText,
            Graphics.TEXT_JUSTIFY_CENTER | Graphics.TEXT_JUSTIFY_VCENTER
        );

        if (!_sleeping) {
            dc.setColor(_palette.accentColor, Graphics.COLOR_TRANSPARENT);
            dc.drawText(
                _layout.ox(),
                _layout.secondsY + _layout.shiftY,
                _layout.secondsFont,
                _data.secondsText,
                Graphics.TEXT_JUSTIFY_CENTER
            );
        }
    }

    function drawStats(dc as Dc) as Void {
        var y = _layout.statsY + _layout.shiftY;
        var labelY = _layout.statsLabelY + _layout.shiftY;
        var left = _layout.leftX + _layout.shiftX;
        var mid = _layout.ox();
        var right = _layout.rightX + _layout.shiftX;

        drawStat(dc, left, y, labelY, _data.heartText, _labelHr);
        drawStat(dc, mid, y, labelY, _data.stepsText, _labelSteps);
        drawStat(dc, right, y, labelY, _data.batteryText, _labelBattery);
    }

    function drawStat(dc as Dc, x as Number, y as Number, labelY as Number, value as String, label as String) as Void {
        dc.setColor(_palette.textColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(x, y, _layout.statsFont, value, Graphics.TEXT_JUSTIFY_CENTER);
        dc.setColor(_palette.mutedColor, Graphics.COLOR_TRANSPARENT);
        dc.drawText(x, labelY, _layout.statsLabelFont, label, Graphics.TEXT_JUSTIFY_CENTER);
    }
}
