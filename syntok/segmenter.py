from typing import Iterator, List, Tuple

import regex

from syntok.tokenizer import Token, Tokenizer
from syntok._segmentation_states import Begin

__PARAGRAPH_SEP = regex.compile("\r?\n(?:\s*\r?\n)+")


def analyze(document: str) -> Iterator[Iterator[List[Token]]]:
    """
    Split a document into paragraphs, sentences, and tokens,
    all the while preserving the offsets of the tokens in the text.

    :param document: to process
    :return: an iterator over paragraphs and sentences as lists of tokens
    """
    tok = Tokenizer()

    for offset, paragraph in preprocess_with_offsets(document):
        tokens = tok.tokenize(paragraph, offset)
        yield segment(tokens)


def process(document: str) -> Iterator[Iterator[List[Token]]]:
    """
    Split a document into paragraphs, sentences, and tokens.

    Note that hyphenated words at linebreaks are joined if appropriate and therefore

    :param document: to process
    :return: an iterator over paragraphs and sentences as lists of tokens
    """
    tok = Tokenizer()

    for paragraph in preprocess(document):
        clean_para = paragraph.replace("\n", " ")
        yield segment(tok.tokenize(clean_para))


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


def split(tokens: Iterator[Token]) -> List[List[Token]]:
    """
    Split Token streams into lists of sentences.

    :param tokens: the Token stream to segment
    :return: a list of Token lists,
             with each Token list representing a sentence
    """
    return list(segment(tokens))


def segment(tokens: Iterator[Token]) -> Iterator[List[Token]]:
    """
    Stream Token streams into sentence streams.

    :param tokens: the Token stream to segment
    :return: an iterator over lists of Tokens,
             with each list representing a sentence
    """
    for state in Begin(tokens):
        if state.at_sentence:
            history = state.collect_history()

            if history and (len(history) > 1 or history[0].value):
                yield history


if __name__ == '__main__':
    import sys

    def do(document: str) -> None:
        for paragraph in process(document):
            for sentence in paragraph:
                print("".join(map(str, sentence)).lstrip())

            print("")

    for filename in sys.argv[1:]:
        with open(filename, 'rt') as handle:
            do(handle.read())

    if len(sys.argv) == 1:
        do(sys.stdin.read())
