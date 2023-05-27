from html.parser import HTMLParser
from typing import NamedTuple


class HtmlInfo(NamedTuple):
    path: str
    title: str
    image: str
    video: str


class HtmlInfoParser(HTMLParser):
    trail: list[tuple[str, list[tuple[str, str | None]]]]
    title: str
    image: str
    video: str
    finished_head: bool

    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.trail = []
        self.title = ""
        self.image = ""
        self.video = ""
        self.finished_head = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.trail.append((tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        if self.trail and self.trail[-1][0] == tag:
            tag, _ = self.trail.pop()
            if tag == "head":
                self.finished_head = True

    def handle_data(self, data: str) -> None:
        if len(self.trail) < 3:
            return
        if self.trail[-2][0] != "head":
            return
        tag, attrs_tuple = self.trail[-1]
        if tag == "title":
            self.title += data
            return

    def handle_startendtag(
        self, tag: str, attrs_tuple: list[tuple[str, str | None]]
    ) -> None:
        if self.image and self.video:
            return
        if tag == "meta":
            attrs = dict(attrs_tuple)
            prop = attrs.get("property")
            if not prop:
                return
            content = attrs.get("content")
            if not content:
                return
            if prop == "og:image":
                self.image = content
            elif prop == "og:video":
                self.video = content


def parse_html_info(prefix_len: int, path: str) -> HtmlInfo:
    with open(path) as file:
        parser = HtmlInfoParser()
        for line in file:
            parser.feed(line)
            if parser.finished_head:
                break

        rel_path = path[prefix_len:]
        return HtmlInfo(
            path=rel_path,
            title=parser.title.strip() or rel_path,
            image=parser.image.strip(),
            video=parser.video.strip(),
        )
