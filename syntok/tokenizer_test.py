import os
from typing import List, Iterable
from unittest import TestCase

from syntok.tokenizer import Tokenizer, Token


def s(tokens: Iterable[Token]) -> List[str]:
    return list(t.value for t in tokens)


class TestTokenizer(TestCase):

    def setUp(self) -> None:
        self.tokenizer = Tokenizer()

    def test_lines(self) -> None:
        with open(os.path.dirname(__file__) + '/tokenizer_test.txt', 'rt', encoding='utf-8') as examples:
            self.examples = examples.readlines()

        error = False

        for i in range(0, len(self.examples), 2):
            line = self.examples[i].strip()
            output = self.examples[i + 1].split()
            result = s(self.tokenizer.split(line))

            if result != output:
                print("expected:", output)
                print("received:", result)
                error = True

        self.assertFalse(error)

    def test_clean_text(self):
        self.assertEqual("He3ll#o", Tokenizer.join_hyphenated_words_across_linebreaks("He3l- \n  l#o"))

    def test_clean_text_Unicode(self):
        for h in Tokenizer._hyphens:
            self.assertEqual("Hello", Tokenizer.join_hyphenated_words_across_linebreaks("Hel" + h + " \n  lo"))

    def test_split_dot(self):
        self.assertListEqual(s(self.tokenizer.split("abc.")), ["abc", "."])

    def test_split_camel_case(self):
        self.assertListEqual(s(self.tokenizer.split("abCd EFG")), ["ab", "Cd", "EFG"])

    def test_hyphens(self):
        for h in Tokenizer._hyphens:
            self.assertListEqual(s(self.tokenizer.split("ab" + h + "cd")), ["ab", "cd"])

        self.tokenizer = Tokenizer(True)

        for h in Tokenizer._hyphens:
            self.assertListEqual(s(self.tokenizer.split("ab" + h + "cd")), ["ab", h, "cd"])

    def test_apostrophes(self):
        for a in Tokenizer._apostrophes:
            self.assertListEqual(s(self.tokenizer.split("ab" + a + "cd")), ["ab", a + "cd"])

    def test_emit_dash(self):
        self.assertListEqual(s(self.tokenizer.split("ab-cd")), ["ab", "cd"])
        self.tokenizer = Tokenizer(True)
        self.assertListEqual(s(self.tokenizer.split("ab-cd")), ["ab", "-", "cd"])

    def test_emit_underscore(self):
        self.assertListEqual(s(self.tokenizer.split("ab_cd")), ["ab", "cd"])
        self.tokenizer = Tokenizer(True)
        self.assertListEqual(s(self.tokenizer.split("ab_cd")), ["ab", "_", "cd"])

    def test_spacing_prefix(self):
        text = " Hi man,  spaces of \u200Ball  kinds!! "
        output = self.tokenizer.split(text)
        reconstruction = "".join(map(str, output))
        self.assertEqual(text, reconstruction)

    def test_inner_ellipsis(self):
        text = "Lalala...or Lala Land...."
        result = self.tokenizer.split(text)
        self.assertListEqual(s(result), ["Lalala", "...", "or", "Lala", "Land", "...", "."])

    def test_nonword_prefix(self):
        text = "..A"
        result = self.tokenizer.split(text)
        self.assertListEqual(s(result), [".", ".", "A"])
        self.assertListEqual([t.offset for t in result], [0, 1, 2])

    def test_nonword_high_prefix(self):
        text = "\U0001F64C.A"
        result = self.tokenizer.split(text)
        self.assertListEqual(s(result), ["\U0001F64C", ".", "A"])
        self.assertListEqual([t.offset for t in result], [0, 1, 2])  # requires Py3.3+

    def test_apostrophe_offset_without_replace_not_contraction(self):
        # NOTE: in this case nothing is replaced, so the offsets should remain identical
        # to those in the original text
        text = "don't"
        self.tokenizer = Tokenizer(replace_not_contraction=False)
        result = self.tokenizer.split(text)
        self.assertListEqual([t.offset for t in result], [0, 2])

    def test_apostrophe_offset_with_replace_not_contraction(self):
        # NOTE: in this case, "n't" is replaced with "not", so a space is introduced.
        # e.g. "don't" -> "do not", "can't" -> "can not"
        text = "don't"
        self.tokenizer = Tokenizer(replace_not_contraction=True)
        result = self.tokenizer.split(text)
        self.assertListEqual([t.offset for t in result], [0, 2])
        self.assertListEqual([t.value for t in result], ["do", "not"])


class TestToText(TestCase):

    def setUp(self) -> None:
        with open(os.path.dirname(__file__) + '/tokenizer_test.txt', 'rt', encoding='utf-8') as examples:
            self.examples = examples.readlines()

    def test_lines(self) -> None:
        self.tokenizer = Tokenizer()
        error = False

        for i in range(0, len(self.examples), 2):
            line = self.examples[i]
            tokens = self.tokenizer.split(line)
            result = Tokenizer.to_text(tokens)

            if result != line.replace("n't", "not"):
                print("expected:", line)
                print("received:", result)
                error = True

        self.assertFalse(error)

    def test_lines_emit_and_do_not_replace(self) -> None:
        self.tokenizer = Tokenizer(True, False)
        error = False

        for i in range(0, len(self.examples), 2):
            line = self.examples[i]
            tokens = self.tokenizer.split(line)
            result = Tokenizer.to_text(tokens)

            if result != line:
                print("expected:", line)
                print("received:", result)
                error = True

        self.assertFalse(error)
