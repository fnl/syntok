from abc import ABCMeta, abstractmethod
from typing import List, Iterator, Optional

from syntok.tokenizer import Token


class State(metaclass=ABCMeta):
    opening_brackets = frozenset("([{\uFF5F\uFF5B\uFF3B\uFF08\uFE5D\uFE5B\uFE59\uFD3E\u301A\u3018\u2985\u2983\u2329")
    """All possible closing brackets that can follow a terminal and still belong to the sentence."""

    closing_brackets = frozenset(")]}\uFF60\uFF5D\uFF3D\uFF09\uFE5E\uFE5C\uFE5A\uFD3F\u301B\u3019\u2986\u2984\u232A")
    """All possible opening brackets with content that might potentially be skipped."""

    closing_quotes = frozenset("'\"\u00B4\u2019\u201D\u232A\u27E9\u27EB\u2E29\u3009\u300B\u301E")
    """All possible closing quotes that can follow a terminal and still belong to the sentence."""

    terminals = frozenset({"..."} | set(".!?\u203C\u203D\u2047\u2048\u2049\u3002\uFE52\uFE57\uFF01\uFF0E\uFF1F\uFF61"))
    """All possible terminal markers."""

    __vowels = "aeiouáéííóúäëïöüåæø"
    vowels = frozenset(__vowels + __vowels.upper())
    """All vowels with accents and umlauts."""

    inner_sentence_punctuation = frozenset(",;:")

    roman_numerals = frozenset("""
    I II III IV V VI VII VIII IX X XI XII XIII XIV XV XVI XVII XVIII XIX XX XXI XXII XXIII XXIV XXV
    """.split())

    months = frozenset("""
    Jän Jan en ene Ene feb febr Feb Mär Mar mzo Mzo Apr abr abl Abr may May jun Jun
    jul Jul ago agto Aug sep Sep sept Sept setbre set oct octbre Oct Okt nov novbre Nov dic dicbre Dic Dez Dec
    """.split())

    abbreviations = frozenset("""
    Abb adm Adm Abs afmo alt Alt Anl ap apdo approx Approx art Art atte atto Aufl ave Ave Az
    bmo Bmo brig Bd Brig bsp Bsp bspw bzgl bzw ca cap capt Capt cf cmdt Cmdt cnel Cnel Co col Col Corp
    de Dr dgl dt emp en es etc evtl excl exca Exca excmo Excmo exsmo Exsmo ff fig Fig figs Figs fr Fr
    gal gen Gen ggf gral Gral GmbH gob Gob Hd hno Hno hnos Hnos Inc incl inkl lic Lic lit ldo Ldo Ltd
    mag Mag max med Med min Mio Mr mr Mrd Mrs mrs Ms ms Mt mt MwSt nat Nat Nr nr ntra Ntra ntro Ntro
    pag phil prof Prof rer Rer resp sci Sci Sr sr Sra sra Srta srta St st synth tab Tab tel Tel
    univ Univ Urt vda Vda vol Vol vs vta zB zit zzgl
    Mon lun Tue mar Wed mie mié Thu jue Fri vie Sat sab Sun dom
    """.split() + list(months))
    """Abbreviations with no dots inside."""

    starters = frozenset("""
    Above Accordingly Additionally Admittedly All Also Although Again And Are As Assuredly Because Besides
    Certainly Chiefly Comparatively Consequently Conversely Coupled Correspondingly Does Due Especially For Furthermore
    Granted Generally Hence How However Identically In Indeed Instead It Its Likewise Moreover Nevertheless No
    Obviously Of On Ordinarily Other Otherwise Outside Particularly Rather
    Similarly Since Singularly Still So Subsequently That The Therefore Thereupon This Thus Unquestionably Use Usually
    What Where Whereas Wherefore Why Yet
    Auch Da Dabei Dadurch Daher Darauf Darum Das Dein Der Deswegen Die Du Ihr Ihnen Er Es Euer
    Ich Mein Nämlich Sie Sein So Somit Sonst Unser Warum Was Wegen Weil Wer Weshalb Wie Wieso Wir
    A Algunas Algunos De Desde Debido El Ella En Hay La Las Los No Otra Otro Para Por Porque Se También Todas Todos
    """.split())
    """Uppercase words that indicate a sentence start."""

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
        return not self.is_empty and (self.__queue[0].value in State.terminals or self.__queue[0].value == "(")

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
    def next_is_an_opening_parenthesis(self) -> bool:
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
    def next_is_inner_sentence_punctuation(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.inner_sentence_punctuation

    @property
    def next_is_month_abbreviation(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.months

    @property
    def next_is_sentence_starter(self) -> bool:
        return not self.is_empty and self.__queue[0].value in State.starters

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

    def find_next_token_after_parenthesis(self, parenthesis) -> Optional[Token]:
        token = None
        parens_stack = parenthesis
        tokens = 1

        while (len(self.__queue) > tokens or self.fetch_next()) and tokens < 50:
            if self._queue[tokens].value in State.opening_brackets:
                parens_stack += self.__queue[0].value
            elif self.__queue[tokens].value in State.closing_brackets:
                parens_stack = parens_stack[:-1]

                if len(parens_stack) == 0:
                    token = self.__queue[tokens]
                    tokens += 1
                    break

            tokens += 1

        return token

    def move_and_skip_parenthesis(self) -> bool:
        if self.move():
            if self.next_is_an_opening_parenthesis:
                parens_stack = self.__queue[0].value
                start = self.__queue[0].offset
                end = -1
                tokens = 1

                while len(self.__queue) > tokens or self.fetch_next():
                    if self._queue[tokens].value in State.opening_brackets:
                        parens_stack += self.__queue[0].value
                    elif self.__queue[tokens].value in State.closing_brackets:
                        parens_stack = parens_stack[:-1]

                        if len(parens_stack) == 0:
                            end = self.__queue[tokens].offset + 1
                            tokens += 1
                            break

                    tokens += 1

                if len(parens_stack) == 0 and end - start < 70:  # TODO: max token len of parenthesis content?
                    self.__history.extend(self.__queue[:tokens])
                    self.__queue = self.__queue[tokens:]

        if not self.__queue:
            return self.fetch_next()
        else:
            return True

    def move_and_maybe_extract_terminal(self, is_first_word_in_sentence: bool) -> 'State':
        # token before the terminal ...
        token_before = self.last
        self.move()
        is_opening_parenthesis = self.last == "("
        offset_in_history = len(self.__history) - 1
        # ... and after the terminal:
        token_after = self.move_to_next_relevant_word_and_return_token_after_terminal()

        # Now decide whether to split:
        if self.next_is_lowercase or self.next_is_inner_sentence_punctuation:
            return self
        # TODO: remove is_first_word_in_sentence and use isinstance(self, FirstToken)
        elif not (is_first_word_in_sentence and self.is_single_letter_or_roman_numeral(token_before)) and \
                self.next_is_sentence_starter:
            return Terminal(self._stream, self._queue, self._history)
        elif token_before in State.abbreviations and \
                token_after not in (self.closing_brackets or self.closing_quotes):
            return self
        elif "." in token_before and token_after != ".":
            return self
        elif self.next_is_numeric and self.next_has_no_spacing:
            return self
        elif token_before.isnumeric() and self.next_is_month_abbreviation:
            return self
        elif (is_first_word_in_sentence or token_before.isupper()) and \
                self.is_single_letter_or_roman_numeral(token_before):
            return self
        else:
            if is_opening_parenthesis:
                old_q = self.__queue
                self.__queue = self._history[offset_in_history:]
                self.__queue.extend(old_q)
                del self.__history[offset_in_history:]
                return Terminal(self._stream, self._queue, self._history)
            else:
                return Terminal(self._stream, self._queue, self._history)

    def is_single_letter_or_roman_numeral(self, token):
        return len(token) == 1 or token in State.roman_numerals

    def move_to_next_relevant_word_and_return_token_after_terminal(self):
        token = None
        # self.last is supposed to be pointing at the terminal right now
        assert self.last in State.terminals

        if self.last == "(":
            token = self.find_next_token_after_parenthesis("(")
        else:
            while self.next_is_a_post_terminal_symbol_part_of_sentence:
                if not self.move():
                    break

                if token is None:
                    token = self.last

            if self.next_is_a_closing_quote and self.next_has_no_spacing:
                if self.move():
                    if token is None:
                        token = self.last

            while self.next_is_a_post_terminal_symbol_part_of_sentence:
                if not self.move():
                    break

                if token is None:
                    token = self.last

            if self.next_is_an_opening_parenthesis:
                idx = 1
                token = None

                while (len(self.__queue) > idx or self.fetch_next()) and \
                        (token is None or token.value in State.opening_brackets):
                    token = self.__queue[idx]
                    idx += 1

        if token is None:
            token = "" if self.is_empty else self.__queue[0]

        # self.last now is supposed to be at the last token of the current sentence
        return token

    @property
    def last(self) -> str:
        if len(self.__history):
            return self.__history[-1].value
        else:
            return ""


class FirstToken(State):

    def __next__(self) -> State:
        if not self.is_empty or self.fetch_next():
            self.move()  # Do not skip parenthesis if they open the sentence.

            if self.next_is_a_terminal:
                return self.move_and_maybe_extract_terminal(True)
            else:
                return InnerToken(self._stream, self._queue, self._history)
        else:
            return End(self._stream, self._queue, self._history)


class InnerToken(State):

    def __next__(self) -> State:
        if not self.is_empty or self.fetch_next():
            self.move_and_skip_parenthesis()

            if self.next_is_a_terminal:
                return self.move_and_maybe_extract_terminal(False)
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
