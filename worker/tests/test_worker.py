from worker import format_message


def test_borrowed_message():
    assert format_message("borrowed", "Ana", "Oscilloscope") == "Ana borrowed Oscilloscope"


def test_returned_message():
    assert format_message("returned", "Ana", "Oscilloscope") == "Ana returned Oscilloscope"


def test_unknown_event_message():
    assert "overdue" in format_message("overdue", "Ana", "Oscilloscope")
