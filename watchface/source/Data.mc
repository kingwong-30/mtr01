import Toybox.Activity;
import Toybox.ActivityMonitor;
import Toybox.Lang;
import Toybox.System;
import Toybox.Time;
import Toybox.Time.Gregorian;

class FaceData {

    var timeText as String = "00:00";
    var secondsText as String = "00";
    var dateText as String = "";
    var heartText as String = "--";
    var stepsText as String = "0";
    var batteryText as String = "--%";
    var minute as Number = 0;

    function initialize() {
    }

    function refresh() as Void {
        var clockTime = System.getClockTime();
        minute = clockTime.min;
        secondsText = clockTime.sec.format("%02d");
        timeText = formatTime(clockTime);
        dateText = formatDate();
        heartText = formatHeartRate();
        stepsText = formatSteps();
        batteryText = formatBattery();
    }

    function formatTime(clockTime as ClockTime) as String {
        var hours = clockTime.hour;
        var minutes = clockTime.min.format("%02d");
        if (System.getDeviceSettings().is24Hour) {
            return Lang.format("$1$:$2$", [hours.format("%02d"), minutes]);
        }
        var h12 = hours % 12;
        if (h12 == 0) {
            h12 = 12;
        }
        return Lang.format("$1$:$2$", [h12.format("%d"), minutes]);
    }

    function formatDate() as String {
        var info = Gregorian.info(Time.now(), Time.FORMAT_MEDIUM);
        return Lang.format("$1$ $2$ $3$", [info.day_of_week, info.day, info.month]);
    }

    function formatHeartRate() as String {
        var activityInfo = Activity.getActivityInfo();
        if (activityInfo != null && activityInfo.currentHeartRate != null) {
            return (activityInfo.currentHeartRate as Number).toString();
        }

        if (ActivityMonitor has :getHeartRateHistory) {
            var history = ActivityMonitor.getHeartRateHistory(1, true);
            if (history != null) {
                var sample = history.next();
                if (sample != null && sample.heartRate != ActivityMonitor.INVALID_HR_SAMPLE) {
                    return sample.heartRate.toString();
                }
            }
        }
        return "--";
    }

    function formatSteps() as String {
        var info = ActivityMonitor.getInfo();
        var steps = 0;
        if (info != null && info.steps != null) {
            steps = info.steps as Number;
        }
        if (steps >= 10000) {
            var thousands = steps / 1000.0;
            return thousands.format("%.1f") + "k";
        }
        return steps.toString();
    }

    function formatBattery() as String {
        var battery = System.getSystemStats().battery;
        return battery.toNumber().toString() + "%";
    }
}
