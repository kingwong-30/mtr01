import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

class KlarApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
    }

    function onStop(state as Dictionary?) as Void {
    }

    function getInitialView() as [Views] or [Views, InputDelegates] {
        return [new KlarView()];
    }

    function onSettingsChanged() as Void {
        WatchUi.requestUpdate();
    }
}

function getApp() as KlarApp {
    return Application.getApp() as KlarApp;
}
