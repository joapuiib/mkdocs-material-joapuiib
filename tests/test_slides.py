from material_joapuiib.plugins.slides import SlidesPlugin


def notes(slides):
    return [[notes for _, notes in vertical] for vertical in slides]


def test_next_notes_follow_linear_order():
    slides = [
        [["s1", "<p>a</p>"]],
        [["s2", "<p>b</p>"], ["s3", "<p>c</p>"]],
    ]

    SlidesPlugin._append_next_notes(slides)

    result = notes(slides)
    assert result[0][0].startswith("<p>a</p><hr>")
    assert result[0][0].endswith("<p>b</p></div>")
    assert result[1][0].startswith("<p>b</p><hr>")
    assert result[1][0].endswith("<p>c</p></div>")
    assert result[1][1] == "<p>c</p>"


def test_next_notes_use_own_notes_only():
    slides = [[["s1", "<p>a</p>"], ["s2", "<p>b</p>"], ["s3", "<p>c</p>"]]]

    SlidesPlugin._append_next_notes(slides)

    assert "<p>c</p>" not in notes(slides)[0][0]


def test_next_notes_without_notes():
    slides = [[["s1", None], ["s2", "<p>b</p>"], ["s3", None]]]

    SlidesPlugin._append_next_notes(slides)

    result = notes(slides)[0]
    assert result[0].startswith("<hr>")
    assert result[1] == "<p>b</p>"
    assert result[2] is None
