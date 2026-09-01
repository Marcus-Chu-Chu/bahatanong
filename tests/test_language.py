from agent.language import detect


def test_english_questions():
    assert detect("Which barangay in Marikina has the most exposed residents?") == "en"
    assert detect("Top 5 cities by exposure share") == "en"


def test_tagalog_questions():
    assert detect("Aling barangay sa Marikina ang may pinakamaraming apektadong residente?") == "tl"
    assert detect("Ano ang sitwasyon ng baha sa Rosario?") == "tl"
    assert detect("Ilan ang paaralan na nasa flood zone sa Pasig?") == "tl"


def test_mixed_defaults_english_without_markers():
    assert detect("Malanday flood stats") == "en"
