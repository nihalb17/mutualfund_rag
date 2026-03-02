import pytest
import os

def test_app_exists():
    """Verify that the Streamlit app file exists."""
    assert os.path.exists("phase_5/app.py")

def test_app_content():
    """Verify that the app contains essential components."""
    with open("phase_5/app.py", "r", encoding="utf-8") as f:
        content = f.read()
        assert "st.set_page_config" in content
        assert "groww-nav" in content
        assert "full_screen" in content
        assert "requests.post" in content
        assert "st.chat_input" in content

def test_ui_styling():
    """Verify that custom Groww colors are defined in CSS."""
    with open("phase_5/app.py", "r", encoding="utf-8") as f:
        content = f.read()
        assert "#00D09C" in content  # Groww Green
        assert "#1E293B" in content  # Dark Header
