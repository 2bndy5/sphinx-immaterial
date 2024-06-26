import pathlib

import pytest

import docutils.nodes
import sphinx
import sphinx.domains.python

if sphinx.version_info < (7, 2):
    from sphinx.testing.path import path as SphinxPath
else:
    from pathlib import Path as SphinxPath  # type: ignore[assignment]

pytest_plugins = ("sphinx.testing.fixtures",)


@pytest.fixture
def theme_make_app(tmp_path: pathlib.Path, make_app):
    conf = """
extensions = [
    "sphinx_immaterial",
]
html_theme = "sphinx_immaterial"
"""

    def make(extra_conf: str = "", **kwargs):
        (tmp_path / "conf.py").write_text(conf + extra_conf, encoding="utf-8")
        (tmp_path / "index.rst").write_text("", encoding="utf-8")
        return make_app(srcdir=SphinxPath(str(tmp_path)), **kwargs)

    yield make


def test_transform_type_annotations_pep604(theme_make_app):
    app = theme_make_app(
        confoverrides=dict(),
    )

    for annotation, expected_text in [
        ("Union[int, float]", "int | float"),
        ("Literal[1, 2, None]", "1 | 2 | None"),
    ]:
        parent = docutils.nodes.TextElement("", "")

        parsed_annotations = sphinx.domains.python._parse_annotation(
            annotation, app.env
        )
        if sphinx.version_info >= (7, 3):
            as_text = "".join([n.astext() for n in parsed_annotations])
            og_parsed = sphinx.domains.python._annotations._parse_annotation(  # type: ignore[module-not-found,attr-defined]
                annotation, app.env
            )
            assert as_text == "".join([n.astext() for n in og_parsed])
            re_exported = sphinx.domains.python._object._parse_annotation(  # type: ignore[module-not-found,attr-defined]
                annotation, app.env
            )
            assert as_text == "".join([n.astext() for n in re_exported])
        parent.extend(parsed_annotations)
        assert parent.astext() == expected_text
