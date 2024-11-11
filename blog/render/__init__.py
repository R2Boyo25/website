from collections.abc import Sequence
import html
import json
import re
from typing import Literal, NotRequired, TypedDict, cast
import emoji
import marko
import marko.element
import marko.inline

from blog.models import Article, Upload


class Italic(TypedDict):
    """HTML `em` tag"""

    type: Literal["italic"]
    content: "InlineNode"


class Bold(TypedDict):
    """HTML `strong` tag"""

    type: Literal["bold"]
    content: "InlineNode"


class Underline(TypedDict):
    """HTML `u` tag"""

    type: Literal["underline"]
    content: "InlineNode"


class Strikethrough(TypedDict):
    """HTML `s` tag"""

    type: Literal["strikethrough"]
    content: "InlineNode"


class InlineCode(TypedDict):
    """HTML inline `code` tag"""

    type: Literal["code"]
    content: str
    lang: NotRequired[str]


class Emoji(TypedDict):
    """Emoji"""

    type: Literal["emoji"]
    name: str


class Link(TypedDict):
    """An HTML `a` tag."""

    type: Literal["link"]
    label: NotRequired["InlineNode"]
    url: str


class Image(TypedDict):
    """An HTML `a` tag."""

    type: Literal["image"]
    alt: NotRequired["InlineNode"]
    source: str


class Raw(TypedDict):
    """Raw HTML export. Unescaped."""

    type: Literal["raw"]
    content: str


InlineNode = (
    str
    | Sequence["InlineNode"]
    | Italic
    | Bold
    | Underline
    | Strikethrough
    | InlineCode
    | Emoji
    | Link
    | Image
    | Raw
)


class Paragraph(TypedDict):
    """HMTL `p` tag"""

    type: Literal["paragraph"]
    content: InlineNode


class Heading(TypedDict):
    """HTML `<h{level}>` tag"""

    type: Literal["heading"]
    level: int
    content: InlineNode


class SubText(TypedDict):
    """HTML `p` tag with the `subtext` class"""

    type: Literal["subtext"]
    content: InlineNode


class Code(TypedDict):
    """HTML `p` tag with the `subtext` class"""

    type: Literal["code"]
    lang: NotRequired[str]
    content: InlineNode


class HorizontalRule(TypedDict):
    """HTML `hr` tag."""

    type: Literal["horizontal_rule"]


class BlockQuote(TypedDict):
    """An HTML blockquote"""

    type: Literal["blockquote"]
    content: "Node"


class List(TypedDict):
    """A list."""

    type: Literal["list"]
    ordered: bool
    items: Sequence["Node"]


Node = (
    Paragraph
    | Heading
    | SubText
    | Raw
    | Code
    | HorizontalRule
    | BlockQuote
    | List
    | Sequence["Node"]
)
IRType = Sequence[Node]


def transform_url(url: str) -> str:
    """Handle links to uploads."""

    if url.startswith("$"):
        upload = Upload.objects.filter(ident=url[1:]).first()

        if upload is not None:
            return upload.path

        else:
            return ""

    return url


class HTMLRenderer:
    """An HTML renderer for my AST format."""

    def __init__(self, data: IRType):
        self.data = data

    @staticmethod
    def get_emoji_tag(unicode_emoji: str) -> str:
        """Converts the `unicode emoji` into an `img` tag with the Twemoji SVG."""

        return (
            '<img class="emoji" src="https://cdnjs.cloudflare.com/ajax/libs/twemoji/15.1.0/svg/'
            + (
                "-".join(
                    [
                        codepoint.lstrip("0")
                        for codepoint in unicode_emoji.encode("unicode_escape")
                        .decode()
                        .split("\\U")
                        if codepoint != ""
                    ]
                )
            )
            + f'.svg" alt="{unicode_emoji}" aria-label="{unicode_emoji}" draggable=false />'
        )

    def flatten_inline(self, inline: InlineNode) -> str:
        """
        Flattens the InlineNode in a safe way.

        Escapes strings
        Join lists of nodes and recursively flatten them.

        For other types of nodes, generate the HTML equivalent for them.
        If a node type is not implemented: returns the empty string
        """

        if isinstance(inline, str):
            text = emoji.emojize(html.escape(inline))
            offset = 0

            for emoji_ in emoji.analyze(text):
                if isinstance(emoji_.value, str):
                    continue

                tag = self.get_emoji_tag(emoji_.chars)

                text = (
                    text[: emoji_.value.start + offset]
                    + tag
                    + text[emoji_.value.end + offset :]
                )

                offset += len(tag) + emoji_.value.start - emoji_.value.end

            return text

        if isinstance(inline, list):
            return "".join(self.flatten_inline(node) for node in inline)

        match inline:
            case {"type": "italic", "content": content}:
                return f"<em>{self.flatten_inline(content)}</em>"

            case {"type": "bold", "content": content}:
                return f"<strong>{self.flatten_inline(content)}</strong>"

            case {"type": "underline", "content": content}:
                return f"<u>{self.flatten_inline(content)}</u>"

            case {"type": "strikethrough", "content": content}:
                return f"<s>{self.flatten_inline(content)}</s>"

            case {"type": "code", "content": content}:

                return f"<code>{html.escape(content)}</code>"

            case {"type": "code", "content": content, "lang": lang}:
                # TODO: inline syntax highlighting???

                return f"<code>{html.escape(content)}</code>"

            case {"type": "emoji", "name": name}:
                for unicode_emoji, names in emoji.EMOJI_DATA.items():
                    if names["en"] == f":{name}:":
                        return self.get_emoji_tag(unicode_emoji)

                return f":{name}:"

            case {"type": "link", "url": url, "label": label}:
                return f'<a href="{html.escape(transform_url(url))}">{self.flatten_inline(label)}</a>'

            case {"type": "link", "url": url}:
                return f'<a href="{html.escape(transform_url(url))}">{html.escape(url)}</a>'

            case {"type": "image", "source": source, "alt": alt}:
                return f'<img src="{html.escape(transform_url(source))}" alt="{self.flatten_inline(alt)}"/>'

            case {"type": "raw", "content": content}:
                return content

        raise NotImplementedError(inline)

    def get_inline_text(self, inline: InlineNode) -> str:
        """
        Extracts the text from inline nodes.

        NOT ESCAPED!
        """

        if isinstance(inline, str):
            return emoji.emojize(inline)

        if isinstance(inline, list):
            return "".join(self.get_inline_text(node) for node in inline)

        match inline:
            case {
                "type": "italic" | "bold" | "underline" | "strikethrough" | "code",
                "content": content,
            }:
                return self.get_inline_text(content)

            case {"type": "emoji", "name": name}:
                for unicode_emoji, names in emoji.EMOJI_DATA.items():
                    if names["en"] == f":{name}:":
                        return unicode_emoji

                return f":{name}:"

            case {"type": "link", "label": label, "url": _url}:
                return self.get_inline_text(label)

            case {"type": "link", "url": url}:
                return url

            case {"type": "raw", "content": content}:
                return content

        raise NotImplementedError(inline)

    def to_html(self, _metadata: Article) -> str:
        """Convert the AST in :py:attr self.data: to an HTML string."""

        return self.flatten_block(self.data)

    def flatten_block(self, node: Node) -> str:
        if isinstance(node, Sequence):
            out = ""

            for node in node:
                out += self.flatten_block(node)

            return out

        match node:
            case {"type": "paragraph", "content": content}:
                return f"<p>{self.flatten_inline(content)}</p>"

            case {"type": "heading", "level": level, "content": content}:
                # TODO: add IDs
                if not isinstance(level, int):
                    raise TypeError("`level` is not an `int`")

                level = min(level, 5)

                heading_id = re.sub(
                    r"--+",
                    "-",
                    "".join(
                        (
                            char.casefold()
                            if char.isalnum() or char in emoji.EMOJI_DATA
                            else "-"
                        )
                        for char in self.get_inline_text(content)
                    ),
                ).strip("-")

                return f'<h{level + 1} id="{heading_id}">{self.flatten_inline(content)}<a style="float: right;" href="#{heading_id}">#</a></h{level + 1}>'

            case {"type": "subtext", "content": content}:
                return f'<p class="subtext">{self.flatten_inline(content)}</p>'

            case {"type": "raw", "content": content}:
                return content

            case {"type": "code", "content": content, "lang": lang}:
                # TODO: syntax highlighting
                return f'<pre><code class="lang-{html.escape(lang)}">{html.escape(self.get_inline_text(content))}</code></pre>'

            case {"type": "code", "content": content}:
                return f"<pre><code>{html.escape(self.get_inline_text(content))}</code></pre>"

            case {"type": "horizontal_rule"}:
                return "<hr />"

            case {"type": "blockquote", "content": content}:
                return f"<blockquote>{self.flatten_block(content)}</blockquote>"

            case {"type": "list", "ordered": ordered, "items": items}:
                xl = "o" if ordered else "u"

                converted_items = "".join(
                    [f"<li>{self.flatten_block(item)}</li>" for item in items]
                )

                return f"<{xl}l>{converted_items}</{xl}l>"

            case _:
                raise NotImplementedError(f"Invalid AST node {node!r}")


def marko_inline_to_ir(element: marko.element.Element | str) -> InlineNode | None:
    """
    Convert a marko inline element or string into an inline node or None
    """

    if isinstance(element, str):
        return element

    if isinstance(element, marko.inline.RawText):
        return element.children

    if isinstance(element, marko.inline.Emphasis):
        return Italic({"type": "italic", "content": convert_inline(element)})

    if isinstance(element, marko.inline.StrongEmphasis):
        return Bold(
            {
                "type": "bold",
                "content": Italic(
                    {"type": "italic", "content": convert_inline(element)}
                ),
            }
        )

    if isinstance(element, marko.inline.CodeSpan):
        if not isinstance(element.children, str):
            raise ValueError("cannot handle inline code block without string child")

        return InlineCode({"type": "code", "content": element.children})

    if isinstance(element, marko.inline.InlineHTML):
        # if isinstance(element.children, Sequence):
        #     raise TypeError(
        #         "why is the child of an inline html element a sequence of markdown elements??????"
        #     )

        return Raw({"type": "raw", "content": element.children})

    if isinstance(element, marko.inline.AutoLink):
        return Link(
            {"type": "link", "url": element.dest, "label": convert_inline(element)}
        )

    if isinstance(element, marko.inline.Link):
        return Link(
            {"type": "link", "url": element.dest, "label": convert_inline(element)}
        )

    if isinstance(element, marko.inline.Image):
        return Image(
            {"type": "image", "source": element.dest, "alt": convert_inline(element)}
        )

    if isinstance(element, marko.inline.LineBreak):
        if not isinstance(element, str):
            return Raw({"type": "raw", "content": "<br />"})

        if not isinstance(element.children, str):
            raise TypeError("why is the child a list of markdown elements")

        return Raw(
            {"type": "raw", "content": element.children.replace("\n", "<br />").strip()}
        )

    raise ValueError(f"Unexpected element {element}")


def convert_inline(
    element: marko.inline.InlineElement | marko.block.BlockElement,
) -> Sequence[InlineNode]:
    """Convert a list of marko inline elements into a list of inline nodes."""

    return [
        el
        for el in [marko_inline_to_ir(el) for el in element.children]
        if el is not None
    ]


def convert_blocks(element: marko.block.BlockElement) -> list[Node]:
    """Convert a list of marko block elements into a list of nodes."""

    return [
        marko_to_ir(el)
        for el in element.children
        if not isinstance(el, marko.block.BlankLine)
    ]


def marko_to_ir(element: marko.element.Element) -> Node:
    """Convert a marko block element into a Node."""

    if isinstance(element, marko.block.BlockElement):
        if isinstance(element, marko.block.Document):
            return cast(Node, convert_blocks(element))

        if isinstance(element, (marko.block.Heading, marko.block.SetextHeading)):
            return Heading(
                {
                    "type": "heading",
                    "level": element.level,
                    "content": convert_inline(element),
                }
            )

        if isinstance(element, marko.block.HTMLBlock):
            return Raw({"type": "raw", "content": element.body})

        if isinstance(element, marko.block.Paragraph):
            return Paragraph({"type": "paragraph", "content": convert_inline(element)})

        if isinstance(element, marko.block.CodeBlock):
            return Code(
                {
                    "type": "code",
                    "content": convert_inline(element),
                }
            )

        if isinstance(element, marko.block.ThematicBreak):
            return HorizontalRule({"type": "horizontal_rule"})

        if isinstance(element, marko.block.Quote):
            return BlockQuote(
                {"type": "blockquote", "content": convert_blocks(element)}
            )

        if isinstance(element, marko.block.FencedCode):
            return Code(
                {
                    "type": "code",
                    "lang": element.lang,
                    "content": convert_inline(element),
                }
            )

        if isinstance(element, marko.block.List):
            return List(
                {
                    "type": "list",
                    "ordered": element.ordered,
                    "items": [
                        convert_blocks(cast(marko.block.BlockElement, item))
                        for item in element.children
                    ],
                }
            )

        if isinstance(element, marko.block.ListItem):
            return convert_blocks(element)

    raise ValueError(f"Unexpected element {element}")


def parse(content: str, content_type: Article.ContentType) -> IRType:
    """Parse article content using the metadata from the article."""

    if content_type == Article.ContentType.JSON:
        return json.loads(content)

    if content_type == Article.ContentType.MARKDOWN:
        return cast(IRType, marko_to_ir(marko.Markdown().parse(content)))

    if content_type == Article.ContentType.HTML:
        return [Raw({"type": "raw", "content": content})]

    raise ValueError(f"Unknown content type: {content_type}")


def render_page(content: str, article: Article) -> str:
    """Render article content using the metadata from the article."""

    parsed = parse(content, Article.ContentType(article.content_type))

    return HTMLRenderer(parsed).to_html(article)
