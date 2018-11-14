from abc import ABCMeta, abstractmethod
from typing import List, Iterator, Optional

from syntok.tokenizer import Token


class State(metaclass=ABCMeta):
    closing_brackets = frozenset(")]}\uFF60\uFF5D\uFF3D\uFF09\uFE5E\uFE5C\uFE5A\uFD3F\u301B\u3019\u2986\u2984\u232A")
    """All possible closing brackets that can follow a terminal and still belong to the sentence."""

    closing_quotes = frozenset("'\"\u00B4\u2019\u201D\u232A\u27E9\u27EB\u2E29\u3009\u300B\u301E")
    """All possible closing quotes that can follow a terminal and still belong to the sentence."""

    terminals = frozenset(".!?\u203C\u203D\u2047\u2048\u2049\u3002\uFE52\uFE57\uFF01\uFF0E\uFF1F\uFF61")
    """All possible terminal markers."""

    __vowels = "aeiouáéííóúäëïöüåæø"
    vowels = frozenset(__vowels + __vowels.upper())
    """All vowels with accents and umlauts."""

    abbreviations = frozenset("""
    ave Ave adm Adm ap approx Approx capt Capt col Col fig Fig figs Figs gal gen Gen
    mag Mag med Med nat Nat phil prof Prof rer Rer sci Sci Sra Srta univ Univ vol Vol
    Jän Jan Ene Feb Mär Mar Apr Abr May Jun Jul Aug Sep Sept Oct Okt Nov Dic Dez Dec
    """.split())
    """Abbreviations with no dots and at least some vowels inside."""

    def __init__(self, stream: Iterator[Token], queue: List[Token], history: List[Token]) -> None:
        self.__stream = stream
        self.__queue = queue
        self.__history = history

    @property
    def _stream(self):
        return self.__stream

    @property
    def _queue(self):
        return self.__queue

    @property
    def _history(self):
        return self.__history

    @property
    def at_sentence(self) -> bool:
        return False

    def collect_history(self) -> Optional[List[Token]]:
        if self.__history:
            sentence = self.__history
            self.__history = []
            return sentence
        else:
            return None

    def __iter__(self) -> Iterator['State']:
        state = self  # type: Optional['State']

        while state is not None:
            yield state
            state = next(state, None)

    @abstractmethod
    def __next__(self) -> 'State':
        raise StopIteration

    @property
    def next_is_a_terminal(self) -> bool:
        return not self.is_empty and (self.__queue[0].value in State.terminals)

    @property
    def next_is_a_potential_abbreviation_marker(self) -> bool:
        return not self.is_empty and self.__queue[0].value == "."

    @property
    def next_is_a_post_terminal_symbol_part_of_sentence(self) -> bool:
        return not self.is_empty and (self.__queue[0].value in State.terminals or
                                      self.__queue[0].value in State.closing_brackets)

    @property
    def next_is_a_closing_quote(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.closing_quotes

    @property
    def next_has_no_spacing(self) -> bool:
        return not self.is_empty and not self.__queue[0].spacing

    @property
    def next_is_lowercase(self) -> bool:
        return not self.is_empty and self.__queue[0].value[:1].islower()

    @property
    def is_empty(self) -> bool:
        return len(self.__queue) == 0

    def fetch_next(self) -> bool:
        t = next(self.__stream, None)

        if t is not None:
            self.__queue.append(t)
            return True
        else:
            return False

    def move(self) -> bool:
        self.__history.append(self.__queue.pop(0))

        if not self.__queue:
            return self.fetch_next()
        else:
            return True

    def move_and_maybe_extract_terminal(self) -> 'State':
        self.move()

        while self.next_is_a_post_terminal_symbol_part_of_sentence:
            if not self.move():
                break

        if self.next_is_a_closing_quote and self.next_has_no_spacing:
            self.move()

        while self.next_is_a_post_terminal_symbol_part_of_sentence:
            if not self.move():
                break

        if self.next_is_lowercase:
            return self
        else:
            return Terminal(self._stream, self._queue, self._history)

    @property
    def last(self) -> str:
        if len(self.__history):
            return self.__history[-1].value
        else:
            return ""


class FirstToken(State):

    def __next__(self) -> State:
        if not self.is_empty or self.fetch_next():
            self.move()
            last = self.last

            if self.next_is_a_terminal and (not self.next_is_a_potential_abbreviation_marker or (last == "I" or (
                    len(last) > 1
                    and last not in State.abbreviations
                    and "." not in last
                    and any(c in State.vowels for c in last)
            ))):
                return self.move_and_maybe_extract_terminal()
            else:
                return InnerToken(self._stream, self._queue, self._history)
        else:
            return End(self._stream, self._queue, self._history)


class InnerToken(State):

    def __next__(self) -> State:
        if not self.is_empty or self.fetch_next():
            self.move()
            last = self.last

            if self.next_is_a_terminal and (not self.next_is_a_potential_abbreviation_marker or (
                    last not in State.abbreviations and
                    last not in ("No", "no") and
                    (last == "." or "." not in last) and
                    (not last.isalnum() or any(c in State.vowels for c in last))
            )):
                return self.move_and_maybe_extract_terminal()
            else:
                return self
        else:
            return End(self._stream, self._queue, self._history)


class Terminal(State):

    @property
    def at_sentence(self) -> bool:
        return len(self._history) > 0

    def __next__(self) -> State:
        if not self.is_empty or self.fetch_next():
            return FirstToken(self._stream, self._queue, self._history)
        else:
            return End(self._stream, self._queue, self._history)


class End(State):

    @property
    def at_sentence(self) -> bool:
        return len(self._history) > 0

    def __next__(self) -> State:
        raise StopIteration


class Begin(State):

    def __init__(self, stream: Iterator[Token]) -> None:
        first_token = next(stream, None)
        queue = [] if first_token is None else [first_token]
        super().__init__(stream, queue, [])

    def __next__(self) -> State:
        if self.is_empty:
            return End(self._stream, self._queue, self._history)
        else:
            return FirstToken(self._stream, self._queue, self._history)
