from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "ui" / "streamlit_app.py"


def find_button(app: AppTest, label: str):
    return next(button for button in app.button if button.label == label)


def test_guided_offline_flow() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=10).run()

    assert [(button.label, button.disabled) for button in app.button] == [
        ("Dashboard", True),
        ("Simulations", True),
        ("Reports", True),
        ("Test", False),
    ]

    find_button(app, "Test").click().run()
    assert find_button(app, "Start environment").disabled is False

    find_button(app, "Start environment").click().run()
    assert app.radio[0].value == "Included call-center sample"
    assert app.selectbox[0].value == "handle_seconds"

    app.selectbox[2].select("Offline").run()
    find_button(app, "Run test").click().run()

    assert not app.exception
    assert any("Test complete" in message.value for message in app.success)
    assert [metric.value for metric in app.metric[-4:]] == ["800", "695", "105", "217.39 seconds"]
