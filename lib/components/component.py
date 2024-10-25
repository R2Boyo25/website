import html
from abc import ABC
from dataclasses import dataclass
import re
from typing import cast


@dataclass
class _Collapse:
    styles: list[tuple[str, str]]
    layout_styles: list[tuple[str, str]]


@dataclass
class Collapse:
    contents: str
    styles: list[str]
    layout_styles: list[str]


class Component(ABC):
    def __init__(self, *children: "Component | str", **kwargs):
        self.children = list(children)

        if "id" in kwargs:
            self.id: str = kwargs["id"]

        if "style" in kwargs:
            self.inline_style: str = kwargs["style"]

        if "class_" in kwargs:
            self.extra_classes: list[str] | str = kwargs["class_"]

    CLASS_PREFIX = "kaz-"

    COMMON: bool = False
    STYLE: str
    LAYOUT_STYLE: str
    CLASS: str
    TAG: str

    def _format_css(self, css: str) -> str:
        lowered = {
            entry.lower(): getattr(self, entry)
            for entry in dir(self)
            if not entry.startswith("_") and not entry.endswith("_")
        }

        if hasattr(self, "CLASS"):
            lowered["class"] = self.CLASS_PREFIX + self.CLASS

        def get_replacement(match: re.Match[str]) -> str:
            return lowered.get(match[1].lower(), "")

        return re.sub(r"\$(\w+)", get_replacement, css)

    def _collapse(self) -> _Collapse:
        styles = []
        layout_styles = []

        for child in self.children:
            if isinstance(child, Component):
                collapsed: _Collapse = child._collapse()

                for style in collapsed.styles:
                    if style not in styles:
                        styles.append((child.CLASS, style))

                for style in collapsed.layout_styles:
                    if style not in layout_styles:
                        layout_styles.append((child.CLASS, style))

        if hasattr(self, "STYLE"):
            if (
                style := (
                    self.CLASS,
                    self._format_css(self.STYLE),
                )
            ) not in styles:
                styles.append(style)

        if hasattr(self, "LAYOUT_STYLE"):
            if (
                style := (
                    self.CLASS,
                    self._format_css(self.LAYOUT_STYLE),
                )
            ) not in layout_styles:
                layout_styles.append(style)

        return _Collapse(styles, layout_styles)

    def collapse(self) -> Collapse:
        collapsed = self._collapse()

        return Collapse(
            str(self),
            [style[1] for style in collapsed.styles],
            [style[1] for style in collapsed.layout_styles],
        )

    def flatten_child(self, child: "str | Component") -> str:
        if isinstance(child, str):
            return html.escape(child)

        return str(child)

    def flatten_children(self) -> str:
        return "".join(self.flatten_child(child) for child in self.children)

    def format_tag(self, tag: str, contents: str, **kwargs) -> str:
        args = "".join(
            f' {key.rstrip("_")}="{value}"'
            for key, value in kwargs.items()
            if value is not None
        )
        return f"<{tag}{args}>{contents}</{tag}>"

    def __str__(self) -> str:
        if hasattr(self, "TAG"):
            if isinstance(
                (extra_classes := getattr(self, "extra_classes", None)), list
            ):
                extra_classes = "".join(f" {class_}" for class_ in extra_classes)

            else:
                extra_classes: str = (" " + getattr(self, "extra_classes", "")).rstrip()

            return self.format_tag(
                self.TAG,
                self.flatten_children(),
                class_=self.CLASS_PREFIX + self.CLASS + extra_classes,
                id_=getattr(self, "id", None),
                style=getattr(self, "inline_style", None),
            )

        return self.flatten_children()


class RawHTML(Component):
    def __init__(self, content: str, **kwargs):
        super().__init__(content, **kwargs)

    def flatten_children(self) -> str:
        return "".join(cast(list[str], self.children))

    def __str__(self) -> str:
        return self.flatten_children()


class Card(Component):
    TAG = "div"
    CLASS = "card"
    STYLE = ".$CLASS { display: flex; border-radius: 12px; flex-direction: center; padding: 16px; background-color: var(--md-sys-color-surface-container-high); gap: 8px; }"


if __name__ == "__main__":
    # print(
    #     Card(
    #         RawHTML('<span title="songs to kill god to" />'),
    #         id="yep",
    #         style="color: red;",
    #         class_=["extra", "classes"],
    #     ).collapse()
    # )

    def recurse_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in recurse_subclasses(c)]
        )

    for component in recurse_subclasses(Component):
        print(getattr(component, "STYLE", None))
