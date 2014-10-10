from djangojs.runners import JsTemplateTestCase, JasmineSuite


class TrackViewerJSTests(JasmineSuite, JsTemplateTestCase):
    template_name = 'tests/track_viewer.html'
