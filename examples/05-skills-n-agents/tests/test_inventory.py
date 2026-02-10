"""Tests for the inventory API."""

import pytest
from api.inventory import track_stock, check_availability, adjust_stock, _stock


@pytest.fixture(autouse=True)
def clear_stock():
    """Clear the in-memory stock store before each test."""
    _stock.clear()
    yield
    _stock.clear()


class TestTrackStock:
    def test_set_stock(self):
        result = track_stock("978-abc", 10)
        assert result["quantity"] == 10
        assert result["status"] == "updated"

    def test_negative_quantity_raises(self):
        with pytest.raises(ValueError, match="Quantity cannot be negative"):
            track_stock("978-abc", -1)


class TestCheckAvailability:
    def test_available(self):
        track_stock("978-abc", 5)
        result = check_availability("978-abc")
        assert result["available"] is True
        assert result["quantity"] == 5

    def test_not_available(self):
        result = check_availability("978-missing")
        assert result["available"] is False
        assert result["quantity"] == 0


class TestAdjustStock:
    def test_add_stock(self):
        track_stock("978-abc", 5)
        result = adjust_stock("978-abc", 3)
        assert result["quantity"] == 8

    def test_remove_stock(self):
        track_stock("978-abc", 5)
        result = adjust_stock("978-abc", -2)
        assert result["quantity"] == 3

    def test_remove_too_many_raises(self):
        track_stock("978-abc", 2)
        with pytest.raises(ValueError, match="Cannot remove"):
            adjust_stock("978-abc", -5)
