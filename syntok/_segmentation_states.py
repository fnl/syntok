from abc import ABCMeta, abstractmethod
from typing import List, Iterator, Optional, Tuple

from syntok.tokenizer import Token


class State(metaclass=ABCMeta):
    opening_brackets = frozenset(
        "([{\uFF5F\uFF5B\uFF3B\uFF08\uFE5D\uFE5B\uFE59\uFD3E\u301A\u3018\u2985\u2983\u2329"
    )
    """
    All possible closing brackets that can follow a terminal
    and still belong to the sentence.
    """

    closing_brackets = frozenset(
        ")]}\uFF60\uFF5D\uFF3D\uFF09\uFE5E\uFE5C\uFE5A\uFD3F\u301B\u3019\u2986\u2984\u232A"
    )
    """All possible opening brackets with content that might potentially be skipped."""

    closing_quotes = frozenset(
        "'\"\u00B4\u2019\u201D\u232A\u27E9\u27EB\u2E29\u3009\u300B\u301E"
    )
    """
    All possible closing quotes that can follow a terminal
    and still belong to the sentence.
    """

    terminals = frozenset(
        {"..."}
        | set(
            ".!?;\u203C\u203D\u2047\u2048\u2049\u3002\uFE52\uFE57\uFF01\uFF0E\uFF1F\uFF61"
        )
    )
    """All possible terminal markers."""

    max_bracket_skipping_length = 70
    """
    Max. num. characters of bracketed text in sentences to ignore when segmenting.

    This helps rapidly move over, e.g., citations as in:
    "This was shown by (A. Author et al.) a few months ago."
    Feel free to alter this value if you would prefer a different length.
    """

    __vowels = "aeiouáéííóúäëïöüåæø"
    vowels = frozenset(__vowels + __vowels.upper())
    """All vowels with accents and umlauts."""

    inner_sentence_punctuation = frozenset(",;:")

    roman_numerals = frozenset(
        """
    I II III IV V VI VII VIII IX X
    XI XII XIII XIV XV XVI XVII XVIII XIX XX
    XXI XXII XXIII XXIV XXV
    """.split()
    )

    months = frozenset(
        """
    Jän Jan en ene Ene feb febr Feb Mär Mar mzo Mzo Apr abr abl Abr may May jun Jun
    jul Jul ago agto Aug sep Sep sept Sept setbre set
    oct octbre Oct Okt nov novbre Nov dic dicbre Dic Dez Dec
    """.split()
    )

    abbreviations = frozenset(
        """
    Abb adm Adm Abs afmo alt Alt Anl ap apdo approx Approx art Art atte atto Aufl ave Ave Az
    bmo Bmo brig Bd Brig bsp Bsp bspw bzgl bzw ca cap capt Capt cf cmdt Cmdt cnel Cnel Co col Col Corp
    de Dr dgl dt emp en es etc evtl excl exca Exca excmo Excmo exsmo Exsmo ff fig Fig figs Figs fr Fr
    gal gen Gen ggf gral Gral GmbH gob Gob Hd hno Hno hnos Hnos Inc incl inkl lic Lic lit ldo Ldo Ltd
    mag Mag max med Med Min min Mio mos Mr mr Mrd Mrs mrs Ms ms Mt mt MwSt nat Nat Nr nr ntra Ntra ntro Ntro
    pag phil prof Prof rer Rer resp sci Sci Sen Sr sr Sra sra Srta srta St st synth tab Tab tel Tel
    univ Univ Urt vda Vda vol Vol vs vta zB zit zzgl
    Mo Mon lun Di Tue mar Mi Wed mie mié Do Thu jue Fr Fri vie Sa Sat sab So Sun dom
    """.split()
    )
    """Abbreviations with no dots inside."""

    starters = frozenset(
        """
    Above Accordingly Additionally Admittedly All
    Also Although Again And Are As Assuredly
    Because Besides
    Certainly Chiefly Comparatively Consequently Conversely Coupled Correspondingly
    Does Due Especially For Furthermore Granted Generally Hence How However
    Identically In Indeed Instead It Its Likewise Moreover Nevertheless No
    Obviously Of On Ordinarily Other Otherwise Outside Particularly Rather
    Similarly Since Singularly Still So Subsequently
    That The Therefore Thereupon This Thus Unquestionably Use Usually
    What Where Whereas Wherefore Why Yet
    Auch Da Dabei Dadurch Daher Darauf Darum Das Dein Der Deswegen Die Du
    Ich Ihr Ihnen Er Es Euer Mein Nämlich Sie Sein So Somit Sonst
    Unser Warum Was Wegen Weil Wer Weshalb Wie Wieso Wir
    A Algunas Algunos De Desde Debido El Ella En Hay La Las Los No
    Otra Otro Para Por Porque Se También Todas Todos
    """.split()
    )
    """Uppercase words that indicate a sentence start."""

    def __init__(
        self, stream: Iterator[Token], queue: List[Token], history: List[Token]
    ) -> None:
        self.__stream = stream
        self.__queue = queue
        self.__history = history

    def collect_history(self) -> Optional[List[Token]]:
        """
        Collect the current production so far.

        If called from a Terminal state, the production will be the sentence.
        """
        if self.__history:
            sentence = self.__history
            self.__history = []
            return sentence
        else:
            return None

    def __iter__(self) -> Iterator["State"]:
        """Move to the next state."""
        state = self  # type: Optional['State']

        while state is not None:
            yield state
            state = next(state, None)

    @abstractmethod
    def __next__(self) -> "State":
        """State transitions to be implemented by the concrete classes."""
        raise StopIteration

    @property
    def _stream(self) -> Iterator[Token]:
        return self.__stream

    @property
    def _queue(self) -> List[Token]:
        return self.__queue

    @property
    def _history(self) -> List[Token]:
        return self.__history

    @property
    def at_sentence(self) -> bool:
        return False

    @property
    def next_is_a_terminal(self) -> bool:
        return not self.is_empty and (
            self.__queue[0].value in State.terminals or self.__queue[0].value == "("
        )

    @property
    def next_is_a_potential_abbreviation_marker(self) -> bool:
        return not self.is_empty and self.__queue[0].value == "."

    @property
    def next_is_a_post_terminal_symbol_part_of_sentence(self) -> bool:
        return not self.is_empty and (
            self.__queue[0].value in State.terminals
            or self.__queue[0].value in State.closing_brackets
        )

    @property
    def next_is_a_closing_quote(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.closing_quotes

    @property
    def next_is_an_opening_bracket(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.opening_brackets

    @property
    def next_has_no_spacing(self) -> bool:
        return not self.is_empty and not self.__queue[0].spacing

    @property
    def next_is_lowercase(self) -> bool:
        return not self.is_empty and self.__queue[0].value[:1].islower()

    @property
    def next_is_numeric(self) -> bool:
        return not self.is_empty and self.__queue[0].value.isnumeric()

    @property
    def next_is_alphanumeric_containing_numeric_char(self) -> bool:
        if self.is_empty:
            return False

        v = self.__queue[0].value
        return (
            any(c.isnumeric() for c in v)
            and v.isalnum()
        )

    @property
    def next_is_a_large_number(self) -> bool:
        if self.is_empty:
            return False

        v = self.__queue[0].value
        return v.isnumeric() and len(v) > 2

    @property
    def next_is_inner_sentence_punctuation(self) -> bool:
        return (
            not self.is_empty
            and self.__queue[0].value in State.inner_sentence_punctuation
        )

    @property
    def next_is_month_abbreviation(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.months

    @property
    def next_is_sentence_starter(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.starters

    @property
    def is_empty(self) -> bool:
        return len(self.__queue) == 0

    @property
    def last(self) -> str:
        """The last token processed and added to histroy, if any."""
        if len(self.__history):
            return self.__history[-1].value
        else:
            return ""

    def _fetch_next(self) -> bool:
        t = next(self.__stream, None)

        if t is not None:
            self.__queue.append(t)
            return True
        else:
            return False

    def __find_next_token_after_bracket(self) -> str:
        """
        Find the next token after a bracketed text that does not look like a sentence,
        when next is an opening bracket.
        """
        closing_bracket, has_inner_sentence = self.__find_end_of_bracketed_text()

        if (
            closing_bracket > 0
            and not has_inner_sentence
            and (len(self.__queue) > closing_bracket + 1 or self._fetch_next())
        ):
            return self.__queue[closing_bracket + 1].value
        else:
            return ""

    def __find_token_after_next(self) -> str:
        """
        Find the token after the next, if it exists.
        """
        len_q = len(self.__queue)

        if len_q > 0:
            if len_q > 1 or self._fetch_next():
                return self.__queue[1].value

        return ""

    def _skip_bracketed_text(self) -> bool:
        """
        Move over bracketed text if not too long and not looking like a sentence,
        when next is an opening bracket.
        """
        assert self.next_is_an_opening_bracket
        closing_bracket, has_inner_sentence = self.__find_end_of_bracketed_text()
        start = self.__queue[0].offset

        if closing_bracket > 0:
            t = self.__queue[closing_bracket]
            end = t.offset + len(t.value)

            if (
                end - start < State.max_bracket_skipping_length
                or not has_inner_sentence
            ):
                self.__history.extend(self.__queue[: closing_bracket + 1])
                self.__queue = self.__queue[closing_bracket + 1:]
                self._fetch_next()
                return True

        return False

    def __find_end_of_bracketed_text(self) -> Tuple[int, bool]:
        """
        Find the index of the closing bracket in the queue (or zero if none)
        and return a flag if the bracket seems to contain a sentence,
        when next is an opening bracket.
        """
        bracket_stack = [self.__queue[0].value]
        queue_idx = 1
        first_is_title = None
        last_is_terminal = False

        while (len(self.__queue) > queue_idx or self._fetch_next()) and queue_idx < 50:
            # check if there is something like an inner sentence inside
            if first_is_title is None and self.__queue[queue_idx].value.isalnum():
                first_is_title = self.__queue[queue_idx].value.istitle()
            elif first_is_title and self.__queue[queue_idx].value.isalnum():
                if len(self.__queue) > queue_idx + 1 or self._fetch_next():
                    last_is_terminal = (
                        self.__queue[queue_idx + 1].value in State.terminals
                    )
                else:
                    last_is_terminal = False

            # stack brackets until the stack is empty
            if self.__queue[queue_idx].value in State.opening_brackets:
                bracket_stack.append(self.__queue[0].value)
            elif self.__queue[queue_idx].value in State.closing_brackets:
                bracket_stack.pop()

                if len(bracket_stack) == 0:
                    break

            queue_idx += 1

        return (
            queue_idx if len(bracket_stack) == 0 else 0,
            bool(first_is_title and last_is_terminal),
        )

    def _move(self) -> bool:
        """Advance the queue, storing the old value in history."""
        self.__history.append(self.__queue.pop(0))

        if not self.__queue:
            return self._fetch_next()
        else:
            return True

    def _move_and_skip_bracketed_text(self) -> bool:
        """Advance the queue, and also skip over bracketed text if applicable."""
        if self._move() and self.next_is_an_opening_bracket:
            self._skip_bracketed_text()

        if not self.__queue:
            return self._fetch_next()
        else:
            return True

    def _move_and_maybe_extract_terminal(self) -> "State":
        """
        If next is a terminal or an opening bracket, advance the queue and
        check whether to transition to the Terminal state.
        """
        # token before the terminal ...
        token_before = self.last

        if not self.next_is_an_opening_bracket:
            self._move()

        # ... and after the terminal:
        token_after = (
            self.__move_to_next_relevant_word_and_return_token_after_terminal()
        )
        # self.last now is the last token of the potential sentence
        # while next is the potential first token of the next sentence

        # Now decide whether to split:
        if self.next_is_lowercase or self.next_is_inner_sentence_punctuation:
            return self  # return self ==> don't split

        elif (
            not (
                isinstance(self, FirstToken)
                and self.is_single_letter_or_roman_numeral(token_before)
            )
            and self.next_is_sentence_starter
        ):  # not a single roman or letter char sentences, and a clear sentence starter
            return Terminal(self._stream, self._queue, self._history)
            # return Terminal ==> split

        elif token_before in State.abbreviations and token_after not in (
            self.closing_brackets or self.closing_quotes
        ):
            return self

        elif token_before in ("no", "No", "NO") and self.next_is_alphanumeric_containing_numeric_char:
            return self

        elif self.next_is_numeric and self.next_has_no_spacing:
            return self

        elif self.next_has_no_spacing and (
                not token_after.istitle()
                or not token_after.isalpha()
                or len(token_after) == 1
        ):
            return self

        elif self.next_is_a_large_number:
            return self

        elif token_before.isnumeric() and self.next_is_month_abbreviation:
            return self

        elif token_before in State.months and self.next_is_numeric:
            return self

        elif "." in token_before and token_after != ".":
            return self

        elif (
            isinstance(self, FirstToken) or token_before.isupper()
        ) and self.is_single_letter_or_roman_numeral(token_before):
            return self

        elif self.is_single_consonant(token_before):
            return self

        elif token_after in State.opening_brackets:
            token_after_brackets = self.__find_next_token_after_bracket()
            token_after_opening_bracket = self.__find_token_after_next()

            if token_after_brackets in State.inner_sentence_punctuation:
                return self
            elif token_after_opening_bracket.istitle():
                return Terminal(self._stream, self._queue, self._history)
            if token_after_brackets[:1].islower():
                return self
            else:
                return Terminal(self._stream, self._queue, self._history)

        else:  # do segment the sentences at this position
            return Terminal(self._stream, self._queue, self._history)

    def __move_to_next_relevant_word_and_return_token_after_terminal(self) -> str:
        """
        If after a terminal and/or next is an opening bracket,
        move to the next token to consider in the queue and
        return the most relevant token value after the terminal.
        """
        assert self.last in State.terminals or self.next_is_an_opening_bracket
        token = None

        if self.next_is_an_opening_bracket and self.last not in State.terminals:
            self._skip_bracketed_text()
        else:
            while self.next_is_a_post_terminal_symbol_part_of_sentence:
                if not self._move():
                    break

                if token is None:
                    token = self.last

            if self.next_is_a_closing_quote and self.next_has_no_spacing:
                if self._move() and token is None:
                    token = self.last

            while self.next_is_a_post_terminal_symbol_part_of_sentence:
                if not self._move():
                    break

                if token is None:
                    token = self.last

            if self.next_is_an_opening_bracket:
                token = self.__queue[0].value  # always return this token
                # do not move yet - we might want the bracket for the next sentence.

        if token is None and (not self.is_empty or self._fetch_next()):
            token = self.__queue[0].value

        return "" if token is None else token

    @staticmethod
    def is_single_letter_or_roman_numeral(token):
        return len(token) == 1 or token in State.roman_numerals

    @staticmethod
    def is_single_consonant(token_before):
        return len(token_before) == 1 and token_before.isalpha() and token_before not in State.vowels


class FirstToken(State):
    def __next__(self) -> State:
        if not self.is_empty or self._fetch_next():
            # If a sentence is opened by parenthesis, treat the whole as its own sentence.
            if self.next_is_an_opening_bracket and self._skip_bracketed_text() and len(self._history) > 3 and not self.next_is_lowercase:
                return Terminal(self._stream, self._queue, self._history)

        if not self.is_empty or self._fetch_next():
            self._move()  # Do not skip parenthesis if they open the sentence.

            if self.next_is_a_terminal:
                return self._move_and_maybe_extract_terminal()
            else:
                return InnerToken(self._stream, self._queue, self._history)
        else:
            return End(self._stream, self._queue, self._history)


class InnerToken(State):
    def __next__(self) -> State:
        if not self.is_empty or self._fetch_next():
            self._move_and_skip_bracketed_text()

            if self.next_is_a_terminal or self.next_is_an_opening_bracket:
                return self._move_and_maybe_extract_terminal()
            else:
                return self
        else:
            return End(self._stream, self._queue, self._history)


class Terminal(State):
    @property
    def at_sentence(self) -> bool:
        return len(self._history) > 0

    def __next__(self) -> State:
        if not self.is_empty or self._fetch_next():
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
