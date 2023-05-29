from abc import ABC
from abc import abstractmethod
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import KW_ONLY
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Mapping
from typing import Sequence
from typing import TypeVar

from termcolor import colored

from .jsonl.reader import Reader
from .templates import get_template
from .utils import needs_generate
from .utils import replace_ext

T = TypeVar("T", bound="AbstractConverter")


@dataclass
class AbstractConverter(ABC):
    ext: ClassVar[str]
    logger: ClassVar[Callable[[str], None]]

    input_filename: str
    force: bool
    _: KW_ONLY
    filename: str = field(init=False)
    generated: bool = field(init=False)

    def __post_init__(self) -> None:
        self.filename = self.create_output_name(self.input_filename)
        self.generated = False
        self._write()

    @classmethod
    def create_output_name(cls, input_filename: str) -> str:
        return replace_ext(input_filename, cls.ext)

    def _needs_generate(self) -> bool:
        if self.force:
            return True
        return needs_generate(self.input_filename, self.filename)

    @abstractmethod
    def generate(self) -> None:
        raise NotImplementedError()

    def _write(self) -> None:
        logger = self.__class__.logger  # mypy is getting it wrong from self.logger
        if not self._needs_generate():
            logger(
                "Up to date: "
                + colored(self.filename, "green")
                + f" (from: {self.input_filename})"
            )
            return

        self.generate()

        logger(
            "Saved: "
            + colored(self.filename, "cyan")
            + f" (from: {self.input_filename})"
        )
        self.generated = False

    @classmethod
    def batch(
        cls: type[T],
        input_filenames: Sequence[str],
        force: bool,
        **kwargs: Any,
    ) -> Sequence[T]:
        return [cls(f, force, **kwargs) for f in input_filenames]


class AbstractJsonlConverter(AbstractConverter):
    template_name: ClassVar[str]

    def generate(self) -> None:
        tmpl = get_template(self.template_name)
        with Reader(self.input_filename) as reader:
            ctx = self.get_template_context(reader)
            with open(self.filename, "w") as out:
                for chunk in tmpl.generate(**ctx):
                    out.write(chunk)

    def get_template_context(self, reader: Reader) -> Mapping[str, object]:
        return {**asdict(self), "reader": reader}
