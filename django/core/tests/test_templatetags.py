from core.templatetags.unit_conversions import distance, speed, category


class TestUnitConversions:

    def test_distance_formats_with_units(self):
        assert distance(100) == "0.05 nmi"

    def test_distance_formats_with_other(self):
        assert distance("") == "error"

    def test_distance_with_none_returns_error(self):
        assert distance() == "error"

    def test_speed_formats_with_units(self):
        assert speed(10) == "19.44 knots"

    def test_speed_formats_with_other(self):
        assert speed("") == "error"

    def test_speed_with_none_returns_error(self):
        assert speed() == "error"

    def test_category_returns_known_category(self):
        assert category('SL') == "Sailing"

    def test_category_returns_unknown_category(self):
        assert category('XX') == "Unknown"

    def test_category_returns_empty_category(self):
        assert category('') == "Unknown"

    def test_category_returns_no_param_category(self):
        assert category() == "error"
