from unittest import TestCase

from syntok import segmenter
from syntok.tokenizer import Token, Tokenizer

DOCUMENT = """Lorem Ipsum

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque auctor id felis a efficitur. Lorem ipsum dolor sit
amet, consectetur adipiscing elit. Suspendisse ac blandit urna. Vestibulum semper nunc id tellus accumsan, at tincidunt
libero dignissim. Praesent enim erat, pellentesque ut condimentum dignissim, dignissim et ligula. Etiam non aliquet
erat, non gravida odio. Suspendisse sit amet varius turpis, at laoreet lectus. Quisque eget pharetra sapien, sit amet
eleifend eros.

Donec pharetra mauris vel molestie sagittis. Mauris_eget_dignissim_arcu. Vestibulum sed interdum orci, in rhoncus
tellus. Aliquam felis odio, varius quis lobortis vel, vulputate vel erat. Donec sed aliquam massa. Donec in enim metus.
Phasellus tristique placerat libero, id vulputate leo tincidunt id.

Sed sagittis, dolor dignissim placerat gravida, nisl nisi bibendum tellus, nec tincidunt est lacus non lacus. Proin
turpis lectus, vulputate non tincidunt non, posuere non ligula. Praesent aliquam ante sed purus lobortis, eu pretium
lectus molestie. Ut quis condimentum ex. Vestibulum molestie pulvinar felis. Sed mollis augue libero, vel dictum lectus
blandit et. In rutrum et tellus eu lacinia. Integer ut tellus eu nunc dapibus pulvinar. Donec et lacinia lorem. Aliquam
eros lacus, eleifend sit amet commodo varius, facilisis ut arcu. In porttitor, urna eu viverra tincidunt, leo nulla
porttitor elit, ac facilisis turpis velit sit amet odio. Etiam rhoncus, mauris eget dictum malesuada, urna sapien
malesuada nulla, et convallis tellus ipsum a felis.

Quisque dapibus mollis leo. Nam a diam sit amet turpis accumsan vestibulum at nec metus. Phasellus dignissim condimentum
elit at feugiat. In elementum non leo id rhoncus. Donec consectetur iaculis diam. Donec nec turpis a nisl tempor tin-
cidunt vel sed neque. Mauris ultricies odio et tempor fermentum. Fusce finibus placerat lorem, in rhoncus ligula
lacinia convallis. Nulla tristique orci sit amet lacus aliquam scelerisque. Nunc consequat urna et nisl feugiat posuere.
Integer pellentesque, mauris et auctor ornare, metus eros euismod sem, id lobortis urna odio quis ante. Suspendisse
blandit suscipit purus, non sodales nibh dignissim vitae.

Aliquam bibendum ultricies convallis. In iaculis, mauris a sodales semper, massa ex maximus ex, a porttitor nunc ipsum
quis neque. Suspendisse urna lectus, accumsan in nulla vel, efficitur porta lorem. Pellent-esque sed arcu nec magna
egestas sollicitudin id eu augue. Sed eget nibh pretium, porta lorem vitae, pharetra ligula. Nunc sed sem sem. Duis a
ipsum hendrerit nisl consectetur hendrerit. Phasellus ante diam, hendrerit vitae porttitor malesuada, maximus vitae
purus. Proin volutpat odio magna, ac convallis massa consectetur sed. Orci varius natoque penatibus et magnis dis
parturient montes, nascetur ridiculus mus.
"""

OSPL = """One sentence per line.
And another sentence on the same line.
(How about a sentence in parenthesis?)
Or a sentence with "a quote!"
'How about those pesky single quotes?'
[And not to forget about square brackets.]
And, brackets before the terminal [2].
You know Mr. Abbreviation I told you so.
What about the med. staff here?
But the undef. abbreviation not.
And this f.e. is tricky stuff.
I.e. a little easier here.
However, e.g., should be really easy.
Three is one btw., is clear.
Their presence was detected by transformation into S. lividans.
Three subjects diagnosed as having something.
What the heck??!?!
(A) First things here.
(1) No, they go here.
[z] Last, but not least.
(vii) And the Romans, too.
Let's meet at 14.10 in N.Y..
This happened in the U.S. last week.
Brexit: The E.U. and the U.K. are separating.
Refugees are welcome in the E.U..
But they are thrown out of the U.K..
And they never get to the U.S..
The U.S. Air Force was called in.
What about the E.U. High Court?
And then there is the U.K. House of Commons.
Now only this splits: the EU.
A sentence ending in U.S. Another that won't split.
12 monkeys ran into here.
Nested (Parenthesis.
(With words inside!
(Right.))
(More stuff.
Uff, this is it!))
In the Big City.
How we got an A.
Mathematics . dot times.
An abbreviation at the end..
This is a sentence terminal ellipsis...
This is another sentence terminal ellipsis....
An easy to handle G. species mention.
Am 13. Jän. 2006 war es regnerisch.
The administrative basis for Lester B. Pearson's foreign policy was developed later.
This model was introduced by Dr. Edgar F. Codd after initial criticisms.
This quote "He said it." is actually inside.
A. The first assumption.
B. The second bullet.
C. The last case.
1. This is one.
2. And that is two.
3. Finally, three, too.
Always last, clear closing example."""

SENTENCES = OSPL.split('\n')
TEXT = ' '.join(SENTENCES)
TOKENIZER = Tokenizer()
SEGMENTED_TOKENS = [TOKENIZER.split(t) for t in SENTENCES]


class TestSegmenter(TestCase):

    def test_segmenter(self):
        self.assertSequenceEqual(SEGMENTED_TOKENS, segmenter.split(TOKENIZER.tokenize(TEXT)))

    def test_simple(self):
        tokens = list(map(lambda v: Token('', v, 0), ["This", "is", "a", "sentence", "."]))
        # noinspection PyTypeChecker
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_empty(self):
        tokens = []
        result = segmenter.split(iter(tokens))
        self.assertEqual([], result)

    def test_one_token(self):
        tokens = [Token("", "I", 0)]
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_two_tokens(self):
        tokens = [Token("", "I", 0), Token("", ".", 1)]
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_two_sentences(self):
        tokens = Tokenizer().split("This is a sentence. This is another sentence.")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_exclamations(self):
        tokens = Tokenizer().split("This is a sentence! This is another sentence!")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_questions(self):
        tokens = Tokenizer().split("Is this a sentence? Is this another sentence?")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_sentences_with_parenthesis_in_second(self):
        tokens = Tokenizer().split("This is a sentence. (This is another sentence.)")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_sentences_with_parenthesis_in_first(self):
        tokens = Tokenizer().split("(This is a sentence.) This is another sentence.")
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_sentences_with_quotes_in_second(self):
        tokens = Tokenizer().split('This is a sentence. "This is another sentence."')
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentence_with_single_quotes(self):
        tokens = Tokenizer().split("This is a sentence. 'This is another sentence.'")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_sentences_with_quotes_in_first(self):
        tokens = Tokenizer().split('"This is a sentence." This is another sentence.')
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_sentences_with_quotes_in_both(self):
        tokens = Tokenizer().split('"This is a sentence." "This is another sentence."')
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_two_sentences_with_quotes_and_prenthesis_in_both(self):
        tokens = Tokenizer().split('"{This is a sentence."} ["This is another sentence."]')
        sep = 9
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_simple_abbreviations(self):
        tokens = Tokenizer().split('This is Mr. Motto here. And here is Mrs. Smithers.')
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_nasty_abbreviations(self):
        tokens = Tokenizer().split('This is Capt. Motto here. And here is Sra. Smithers.')
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_special_abbreviations(self):
        tokens = Tokenizer().split('This f.e. here. And here is med. help.')
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_nasty_special_abbreviations(self):
        tokens = Tokenizer().split('This f. e. here. And here is unknwn. help.')
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_enumerations(self):
        tokens = Tokenizer().split('1. This goes first. 2. And here thereafter.')
        sep = 6
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_one_word_sentences(self):
        tokens = Tokenizer().split('Who did this? I. No! Such a shame.')
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:4], tokens[4:6], tokens[6:8], tokens[8:]], result)

    def test_brackets_before_the_terminal(self):
        tokens = Tokenizer().split("Brackets before the terminal [2]. You know I told you so.")
        sep = 8
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentence_marker_after_abbreviation(self):
        tokens = Tokenizer().split("Let's meet at 14.10 in N.Y.. This happened in the U.S. last week.")
        sep = 9
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)


class TestPreprocess(TestCase):

    def test_preprocess_with_offsets(self):
        text = " ab\n \n cd- \n \n ef \n\n"
        result = segmenter.preprocess_with_offsets(text)
        self.assertListEqual([(0, " ab"), (6, " cd- "), (14, " ef "), (20, "")], result)

    def test_preprocess(self):
        text = " ab\n \n  cd- \n\n ef \n\n"
        result = segmenter.preprocess(text)
        self.assertListEqual([" ab", "  cdef ", ""], result)


class TestAnalyze(TestCase):

    def test_analyze(self):
        offset = 0

        for paragraph in segmenter.analyze(DOCUMENT):
            for sentence in paragraph:
                for token in sentence:
                    if token.value:
                        offset = DOCUMENT.index(token.value, offset)
                        self.assertEqual(offset, token.offset, repr(token))
                        offset += len(token.value)


class TestProcess(TestCase):

    def test_process(self):
        for paragraph in segmenter.process(DOCUMENT):
            offset = 0

            for sentence in paragraph:
                for token in sentence:
                    if token.value and token.value != "tincidunt":  # tin-cidunt linebreak!
                        new_offset = DOCUMENT.find(token.value, offset)
                        self.assertNotEqual(new_offset, -1,
                                            repr(token) + " at %d" % offset)
                        offset = new_offset + len(token.value)
