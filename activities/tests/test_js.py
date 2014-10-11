from djangojs.runners import JsTemplateTestCase, JasmineSuite


class TrackViewerJSTests(JasmineSuite, JsTemplateTestCase):
    template_name = 'tests/track_viewer.html'


class SpeedViewerJSTests(JasmineSuite, JsTemplateTestCase):
    template_name = 'tests/speed_viewer.html'
