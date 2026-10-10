from pathlib import Path
from streamlit.testing.v1 import AppTest
APP = str(Path(__file__).resolve().parents[1] / 'app.py')

def test_navigation_search_theme_and_detail():
    at = AppTest.from_file(APP, default_timeout=15).run()
    assert not at.exception
    assert at.metric[0].value == '8'
    for name in ['All files','Smart collections','Duplicate files','Recently analyzed','Organization plan','Add files','Settings','Overview']:
        at.button(key='nav_'+name).click().run()
        assert not at.exception, name
    at.toggle(key='dark').set_value(True).run()
    assert not at.exception
    at.text_input(key='search').set_value('photosynthesis').run()
    assert len([b for b in at.button if (b.key or '').startswith('open_')]) == 2
    next(b for b in at.button if (b.key or '').startswith('open_')).click().run()
    assert not at.exception
    assert 'Photosynthesis' in at.text_area[0].value
