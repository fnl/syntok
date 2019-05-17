from typing import Iterator, List, Tuple

import regex

from syntok._segmentation_states import Begin, State
from syntok.tokenizer import Token, Tokenizer

__PARAGRAPH_SEP = regex.compile("\r?\n(?:\\s*\r?\n)+")


def analyze(document: str, bracket_skip_len=None) -> Iterator[Iterator[List[Token]]]:
    """
    Segment a document into paragraphs, sentences, and tokens,
    all the while preserving the offsets of the tokens in the text.

    Hyphenated words at linebreaks are still treated as two separate
    tokens when using this function, and the original input document
    `str` value is producible from the `Token` spacing and values.

    :param document: to process
    :param bracket_skip_len: n. chars of bracketed text inside sentences to skip over
    :return: an iterator over paragraphs and sentences as lists of tokens
    """
    tok = Tokenizer(replace_not_contraction=False)

    for offset, paragraph in preprocess_with_offsets(document):
        tokens = tok.tokenize(paragraph, offset)
        yield segment(tokens, bracket_skip_len)


def process(document: str, bracket_skip_len=None) -> Iterator[Iterator[List[Token]]]:
    """
    Segment a document into paragraphs, sentences, and tokens.

    Note that hyphenated words at linebreaks are joined and
    negation contractions ("don't") are replaced with "do" and "not",
    therefore the original input document might not be reproducible.

    :param document: to process
    :param bracket_skip_len: n. chars of bracketed text inside sentences to skip over
    :return: an iterator over paragraphs and sentences as lists of tokens
    """
    tok = Tokenizer()

    for paragraph in preprocess(document):
        yield segment(tok.tokenize(paragraph), bracket_skip_len)


def preprocess(text: str) -> List[str]:
    """
    Split text bodies into paragraphs and
    join hyphenated words across line-breaks.

    :param text: to preprocess
    :return: a list of paragraphs
    """
    return __PARAGRAPH_SEP.split(
        Tokenizer.join_hyphenated_words_across_linebreaks(text)
    )


def preprocess_with_offsets(text: str) -> List[Tuple[int, str]]:
    """
    Split text bodies into (offset, paragraph) Tuples.

    Unlike `preprocess(str)` this does *not* join hyphenated words,
    to preserve the text in an as pristine state as possible.

    :return: a list of (offset, paragraph) Tuples
    """

    def finditer():
        offset = 0

        for mo in __PARAGRAPH_SEP.finditer(text):
            yield (offset, text[offset:mo.start()])
            offset = mo.end()

        yield (offset, text[offset:])

    return list(finditer())


def split(tokens: Iterator[Token], bracket_skip_len=None) -> List[List[Token]]:
    """
    Split Token streams into lists of sentences.

    :param tokens: the Token stream to segment
    :param bracket_skip_len: n. chars of bracketed text inside sentences to skip over
    :return: a list of Token lists,
             with each Token list representing a sentence
    """
    return list(segment(tokens, bracket_skip_len))


def segment(tokens: Iterator[Token], bracket_skip_len=None) -> Iterator[List[Token]]:
    """
    Stream Token streams into sentence streams.

    :param tokens: the Token stream to segment
    :param bracket_skip_len: n. chars of bracketed text inside sentences to skip over
    :return: an iterator over lists of Tokens,
             with each list representing a sentence
    """
    if bracket_skip_len is not None:
        State.max_bracket_skipping_length = int(bracket_skip_len)

    for state in Begin(tokens):
        if state.at_sentence:
            history = state.collect_history()

            if history and (len(history) > 1 or history[0].value):
                yield history


if __name__ == "__main__":
    import sys

    def do(document: str) -> None:
        for paragraph in process(document):
            for sentence in paragraph:
                print("".join(map(str, sentence)).lstrip())

            print("")

    for filename in sys.argv[1:]:
        with open(filename, "rt") as handle:
            do(handle.read())

    if len(sys.argv) == 1:
        do(sys.stdin.read())
