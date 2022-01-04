from typing import Iterator, List, Generator

import regex


class Token:
    """
    A string wrapper with a `spacing` attribute that
    describes the prefix after which this token was split
    and an `offset` attribute to describe its position in
    the text being tokenized.

    Typically, the prefix will be a single whitespace character, but it
    can be really anything found between the current and the last token
    (or anything before the first token in the text).

    The offset represents the Token's position in the original text.

    Two Tokens are equal if they share the same value,
    no matter their spacing and offsets.
    """

    def __init__(self, space_prefix: str, value: str, offset: int) -> None:
        self._spacing = space_prefix
        self._value = value
        self._offset = offset

    def __repr__(self) -> str:
        return "<Token %s : %s @ %d>" % (
            repr(self._spacing),
            repr(self._value),
            self._offset
        )

    def __str__(self) -> str:
        return "%s%s" % (self._spacing, self._value)

    def __eq__(self, other) -> bool:
        if other is None or not isinstance(other, Token):
            return False

        return other._value == self._value

    def __hash__(self) -> int:
        return hash(self._value)

    @property
    def value(self) -> str:
        """The Token's actual value."""
        return self._value

    @property
    def spacing(self) -> str:
        """The spacing that prefixed the Token in the text."""
        return self._spacing

    @property
    def offset(self) -> int:
        """The offset of the Token in the text."""
        return self._offset

    def update(self, val: int) -> None:
        """Update the offset of the Token by adding `val`."""
        self._offset += val


class Tokenizer:
    # noinspection PyUnresolvedReferences
    """ Split strings into syntactic Tokens. """

    _hyphens = "\u00AD\u058A\u05BE\u0F0C\u1400\u1806\u2010\u2011\u2012\u2e17\u30A0-"
    """Hyphen Unicode chars to be aware of when splitting."""

    _hyphens_and_underscore = frozenset(_hyphens + "_")
    """The set of all hyphen Unicode chars and the underscore."""

    _hyphen_newline = regex.compile(r"(?<=\p{L})[" + _hyphens + "][ \t\u00a0\r]*\n[ \t\u00a0]*(?=\\p{L})")
    """A token split across a newline with a hyphen marker."""

    _apostrophes = "'\u00B4\u02B9\u02BC\u2019\u2032"
    """Apostrophe Unicode chars to be aware of when splitting."""

    _apostrophe_t = regex.compile('[' + _apostrophes + ']t')
    """Apostrophe-t regex, to detect "n't" suffixes."""

    # about 25% of the runtime of the tokenizer is spent with this regex
    _separation = regex.compile(
        r"(?<=\p{Ll})[.!?]?(?=\p{Lu})|" +  # lowercase-uppercase transitions
        r"[" + _apostrophes + r"]\p{L}+|" +  # apostrophes and their tail
        r"[\p{Ps}\p{Pe}]|" +   # parenthesis and open/close punctuation
        r"\.\.\.|" +  # inner ellipsis
        r"(?<=\p{L})[,;_" + _hyphens + r"](?=[\p{L}\p{Nd}])|" +  # dash-not-digits transition prefix
        r"(?<=[\p{L}\p{Nd}])[,;_" + _hyphens + r"](?=\p{L})"  # dash-not-digits transition postfix
    )
    """Secondary regex to sub-split non-whitespace sequences."""

    # Annoyingly, unicode regex character class \S does not include the zwsp...
    _spaces = regex.compile(r"[^\s\u200b]+", regex.UNICODE)
    """Primary regex to split strings at any kind of Unicode whitespace and the zero width space (zwsp)."""

    @staticmethod
    def join_hyphenated_words_across_linebreaks(text: str) -> str:
        """Join 'hyhen-\\n ated wor- \\nds' to 'hyphenated words'."""
        return Tokenizer._hyphen_newline.subn("", text)[0]

    @staticmethod
    def to_text(tokens: List[Token]) -> str:
        """
        Reconstruct the original text where the Tokens were found.

        This works because a Token stores its spacing prefix.
        """
        return "".join(map(str, tokens))

    def __init__(
        self, emit_hyphen_or_underscore_sep: bool = False, replace_not_contraction: bool = True
    ):
        """
        Set tuning options around hyphens & underscores, and "n't" contractions.

        Note that hyphens and underscores are, if not emitted,
        set as the `Token.spacing` values, but they are never "lost".

        :param emit_hyphen_or_underscore_sep: as separate tokens
                                              if found as single char inside words
        :param replace_not_contraction: replace "n't" with "not" (by default)
        """
        self.emit_hyphen_underscore_sep = emit_hyphen_or_underscore_sep
        self.replace_not_contraction = replace_not_contraction

    def split(self, text: str) -> List[Token]:
        """Extract the list of Tokens from `text`."""
        return list(self.tokenize(text))

    def tokenize(self, text: str, base_offset: int = 0) -> Iterator[Token]:
        """Generate Tokens from the `text`."""
        if base_offset > 0:
            text = " " * base_offset + text

        offset = base_offset

        for mo in Tokenizer._spaces.finditer(text):
            start = Tokenizer._find_start(mo.start(), mo.end(), text)

            if start == mo.end():
                yield Token(text[offset:mo.start()], mo.group(0), mo.start())
            else:
                end = Tokenizer._find_end(start, mo.end(), text)

                if start > mo.start():
                    offset = yield from self._split_nonword_prefix(mo, offset, start, text)

                if start != end:
                    yield from self._split_word(text[offset:start], text[start:end], start)

                tail = text[end:mo.end()]

                if tail.startswith("..."):
                    yield Token("", "...", end)
                    end += 3
                    tail = tail[3:]

                yield from [Token("", c, idx + end) for idx, c in enumerate(tail)]

            offset = mo.end()

        if offset < len(text):
            yield Token(text[offset:], "", len(text))

    @staticmethod
    def _find_start(start: int, end: int, text: str) -> int:
        for c in range(start, end):
            if text[c].isalnum():
                break

            start += 1

        return start

    @staticmethod
    def _find_end(start: int, end: int, text: str) -> int:
        for c in range(end - 1, start - 1, -1):
            if text[c].isalnum():
                break

            end -= 1

        return end

    @staticmethod
    def _split_nonword_prefix(mo, offset: int, start: int, text: str) -> Generator[Token, None, int]:
        """Yield separate tokens for each non-alnum symbol prefixing an alnum word."""
        for i, c in enumerate(text[mo.start():start]):
            if i == 0:
                yield Token(text[offset:mo.start()], c, mo.start())
                offset = start
            else:
                yield Token("", c, mo.start() + i)

        return offset

    def _split_word(self, prefix: str, word: str, offset: int) -> Iterator[Token]:
        """Yield separate tokens alnum words if they contain `_separation` patterns."""
        remainder = 0

        for mo in Tokenizer._separation.finditer(word):
            prefix = yield from self._produce_separator_split_token(remainder, word, mo, prefix, offset)
            remainder = mo.end()

        if remainder == 0:
            yield Token(prefix, word, offset)
        elif remainder < len(word):
            yield Token(prefix, word[remainder:], offset + remainder)

    def _produce_separator_split_token(
            self, remainder: int, word: str, mo: regex, prefix: str, offset: int
    ) -> Generator[Token, None, str]:
        """Helper method to handle alnum words with `_separation` patterns."""
        if mo.start() > remainder:
            if Tokenizer._apostrophe_t.fullmatch(mo.group(0)) and word[mo.start() - 1] == 'n':
                if remainder < mo.start() - 1:
                    yield Token(prefix, word[remainder:mo.start() - 1], offset + remainder)
                    prefix = ""

                yield Token(prefix, "not" if self.replace_not_contraction else 'n' + mo.group(0), offset + mo.start() - 1)
                return ""

            yield Token(prefix, word[remainder:mo.start()], offset + remainder)
            prefix = ""

        separator = mo.group(0)

        if separator and self._can_emit(separator):
            yield Token(prefix, separator, offset + mo.start())
            return ""
        else:
            return prefix + separator

    def _can_emit(self, separator: str):
        """Verify if the alnum word `separator` can be emitted with this Tokenizer."""
        return self.emit_hyphen_underscore_sep or \
               separator not in Tokenizer._hyphens_and_underscore


if __name__ == '__main__':
    import sys

    tok = Tokenizer()

    if len(sys.argv) > 1:
        for filename in sys.argv[1:]:
            with open(filename, 'rt') as stream:
                for line in stream:
                    print(" ".join(t.value for t in tok.tokenize(line)))
    else:
        for line in sys.stdin:
            print(" ".join(t.value for t in tok.tokenize(line)))
