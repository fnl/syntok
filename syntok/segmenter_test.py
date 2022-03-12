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
A sentence ending in U.S. Another that will not split.
(A parenthesis at sentence start.)
Do not begin sentences with parenthesis.
(As that ends with) a world of pain.
Alexandri Aetoli Testimonia et Fragmenta.
Studi e Testi 15.
(1999) This (1999) gets merged because indistinguishable from enumeration.
12 monkeys ran into here.
Nested (Parenthesis. (With words inside! (Right.)) (More. This is it!))
In the Big City.
(This is a very long sentence inside parenthesis.
Followed by another, so we want to split them.)
How we got an A. Mathematics . dot times.
An abbreviation at the end..
This is a sentence terminal ellipsis...
This is another sentence terminal ellipsis....
An easy to handle G. species mention.
Am 13. Jän. 2006 war es regnerisch.
And on Jan. 22, 2022 it was, too.
(Phil. 4:8)
(Oh. Again!)
Syntok even handles bible quotes!
The basis for Lester B. Pearson's policy was later.
This model was introduced by Dr. Edgar F. Codd after initial criticisms.
This quote "He said it." is actually inside.
B. Obama fas the first black US president.
A. The first assumption.
B. The second bullet.
C. The last case.
1. This is one.
2. And that is two.
3. Finally, three, too.
A 130 nm CMOS power amplifier (PA) operating at 2.4 GHz.
Its power stage is composed of a set of amplifying cells.
Specimens (n = 32) were sent for 16S rRNA PCR.
16S rRNA PCR could identify an organism in 10 of 32 cases (31.2%).
Cannabis sativa subsp. sativa at Noida was also confirmed.
Eight severely CILY-affected villages of Grand-Lahou in 2015.
Leaves, inflorescences and trunk borings were collected.
Disturbed the proper intracellular localization of TPRBK.
Moreover, the knockdown of TPRBK expression.
Elevated expression of LC3.
Importantly, immunohistochemistry analysis revealed it.
Bacterium produced 45U/mL -mannanase at 50 degrees C.
The culture conditions for high-level production.
Integration (e.g., on-chip etc.), can translate to lower cost.
The invasive capacity of S. Typhi is high.
Most pRNAs have a length of 8-15 nt, very few up to 24 nt.
The average length of pRNAs tended to increase from stationary to outgrowth conditions.
Results: In AAA, significantly enhanced mRNA expression was observed (p <= .001).
MMPs with macrophages (p = .007, p = .018, and p = .015, resp.).
And synth. muscle cells with MMPs (p = .020, p = .018, and p = .027, respectively).
(C) 2017 Company Ltd.
All rights reserved.
(C) 2017 Company B.V.
All rights reserved.
Northern blotting and RT-PCR.
C2m9 and C2m45 carried missense mutations.
The amplifier consumes total DC power of 167 uW.
The input-referred noise is 110 nV/sqrt(Hz).
Inflammation via activation of TLR4.
We also identify a role for TLR4.
Effects larger (eta(2) = .53), with cognition (eta(2) = .14) and neurocognition (eta(2) = .16).
All validations show a good approximation of the behavior of the DMFC.
In addition, a simulated application of a circuit system is explained.
Conclusions: Our data suggest CK5/6, CK7, and CK18 in the subclassification of NSCLC.
Copyright (C) 2018 S. Korgur AG, Basel.
Gelatin degradation by MMP-9.
ConclusionThis study provides clear evidence.
A sampling frequency of 780 MHz.
The figure-of-merit of the modulator is there.
Patients with prodromal DLB.
In line with the literature on DLB.
This is verse 14;45 in the test;
Splitting on semi-colons.
The discovery of low-mass nulceli (AGN; NGC 4395 and POX 52; Filippenko & Sargent 1989; Kunth et al. 1987) triggered a quest; it has yielded today more than 500 sources.
The Company is the No. 2 and No. 3 largest chain in the U.S. and Canada, respectively, by number of stores.
Always last, clear closing example."""

SENTENCES = OSPL.split("\n")
TEXT = " ".join(SENTENCES)
TOKENIZER = Tokenizer()
SEGMENTED_TOKENS = [TOKENIZER.split(t) for t in SENTENCES]


class TestSegmenter(TestCase):
    def test_segmenter(self):
        def make_sentences(segmented_tokens):
            for sentence in segmented_tokens:
                yield "".join(str(token) for token in sentence).strip()

        self.maxDiff = None
        expected = "\n".join(make_sentences(SEGMENTED_TOKENS))
        received = "\n".join(make_sentences(segmenter.split(TOKENIZER.tokenize(TEXT))))
        assert expected == OSPL
        assert expected == received
        assert SEGMENTED_TOKENS == segmenter.split(TOKENIZER.tokenize(TEXT))

    def test_simple(self):
        tokens = list(
            map(lambda v: Token("", v, 0), ["This", "is", "a", "sentence", "."])
        )
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
        tokens = Tokenizer().split(
            '{"This is a sentence."} ["This is another sentence."]'
        )
        sep = 9
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_simple_abbreviations(self):
        tokens = Tokenizer().split("This is Mr. Motto here. And here is Mrs. Smithers.")
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_common_abbreviations(self):
        tokens = Tokenizer().split("Warran supports Min. Wage Workers. Sen. Elizabeth Warren called on Biden.")
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_single_letter_abbreviations(self):
        tokens = Tokenizer().split(
            "The case is Nath v. Lightspeed Commerce"
        )
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_sentences_with_nasty_abbreviations(self):
        tokens = Tokenizer().split(
            "This is Capt. Motto here. And here is Sra. Smithers."
        )
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_special_abbreviations(self):
        tokens = Tokenizer().split("This f.e. here. And here is med. help.")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_nasty_special_abbreviations(self):
        tokens = Tokenizer().split("This f. e. here. And here is unknwn. help.")
        sep = 7
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_ending_with_false_positive_month_abbreviation_1(self):
        tokens = Tokenizer().split(
            "Some of the cookies are essential for parts of the site to operate and have already been set. You may delete and block all cookies from this site, but if you do, parts of the site may not work."
        )
        sep = 19
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_ending_with_false_positive_month_abbreviation_2(self):
        tokens = Tokenizer().split(
            "The sharpshooter appears to be checked out on his Kings experience, and an argument could easily be raised that he should have been moved two years ago. Now, his $23 million salary will be a tough pill for teams to swallow, even if there is decent chance of a solid bounce-back year at a new destination."
        )
        sep = 29
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_enumerations(self):
        tokens = Tokenizer().split("1. This goes first. 2. And here thereafter.")
        sep = 6
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_letter_enumerations(self):
        tokens = Tokenizer().split("A. This goes first. B. And here thereafter.")
        sep = 6
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentences_with_Roman_enumerations(self):
        tokens = Tokenizer().split("I. This goes first. II. And here thereafter.")
        sep = 6
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_one_word_sentences(self):
        tokens = Tokenizer().split("Who did this? I. No! Such a shame.")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:4], tokens[4:8], tokens[8:]], result)

    def test_brackets_before_the_terminal(self):
        tokens = Tokenizer().split(
            "Brackets before the terminal [2]. You know I told you so."
        )
        sep = 8
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentence_marker_after_abbreviation(self):
        tokens = Tokenizer().split(
            "Let's meet at 14.10 in N.Y.. This happened in the U.S. last week."
        )
        sep = 9
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentence_ends_in_abbreviation(self):
        tokens = Tokenizer().split("operating at 2.4 GHz. Its power stage")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentence_ends_in_single_letter_and_starts_with_starter_word(self):
        tokens = Tokenizer().split("got an A. And then he")
        sep = 4
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_split_with_dot_following_abbreviation(self):
        tokens = Tokenizer().split("in the E.U.. But they are")
        sep = 5
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_split_with_complext_abbreviation_pattern(self):
        tokens = Tokenizer().split("resp.). Indicate")
        sep = 4
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_sentence_with_abbreviation_indictated_by_punctuation(self):
        tokens = Tokenizer().split("Don't splt., please!")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_sentence_with_abbreviation_with_dot(self):
        tokens = Tokenizer().split("The U.S. Air Force is here.")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_sentence_with_single_letter_abbreviation(self):
        tokens = Tokenizer().split(
            "The basis for Lester B. Pearson's policy was later."
        )
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_sentence_with_single_letter_at_end(self):
        # Sadly, this one cannot split if we want to capture author abbreviations
        tokens = Tokenizer().split("got an A. Mathematics was")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_abbreviation_followed_by_large_number(self):
        tokens = Tokenizer().split("This is abcf. 123 here.")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_abbreviation_no_followed_by_alnum_token(self):
        tokens = Tokenizer().split("This is no. A13 here.")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_abbreviation_followed_by_parenthesis(self):
        tokens = Tokenizer().split("This is abcf. (123) in here.")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_do_not_split_bible_citation(self):
        tokens = Tokenizer().split("This is a bible quote? (Phil. 4:8) Yes, it is!")
        result = segmenter.split(iter(tokens))
        self.assertEqual(len(result[0]), 6)
        self.assertEqual(len(result[1]), 5)
        self.assertEqual(len(result[2]), 5)

    def test_split_self_standing_parenthesis(self):
        tokens = Tokenizer().split("Studi e Testi 15. (1999)")
        result = segmenter.split(iter(tokens))
        self.assertEqual(len(result[0]), 5)
        self.assertEqual(len(result[1]), 3)

    def test_do_not_split_short_text_inside_parenthesis(self):
        tokens = Tokenizer().split(
            "This is (Proc. ABC with Abs. Reg. Compliance) not here."
        )
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_do_not_split_short_text_inside_parenthesis3(self):
        tokens = Tokenizer().split(
            "ET in the 112 ER+ patients (HR=2.79 for high CCNE1, p= .005 and .HR=1.97 for CCNE2, p= .05) is wrong."
        )
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_do_not_split_short_text_inside_parenthesis4(self):
        tokens = Tokenizer().split(
            "This was shown by (A. Author et al.) a few months ago."
        )
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_split_long_text_inside_parenthesis(self):
        tokens = Tokenizer().split(
            "This is one. (Here is another view of the same. And then there is a different case here.)"
        )
        sep1 = 4
        sep2 = 13
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep1], tokens[sep1:sep2], tokens[sep2:]], result)

    def test_split_long_text_inside_parenthesis2(self):
        tokens = Tokenizer().split(
            "This is one (Here is another view of the same. And then there is a different case here.)"
        )
        sep1 = 3
        sep2 = 12
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep1], tokens[sep1:sep2], tokens[sep2:]], result)

    def test_split_sentence_with_parenthesis_at_start(self):
        tokens = Tokenizer().split("A sentences here. (This is) a world of pain.")
        sep = 4
        result = segmenter.split(iter(tokens))
        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 4)
        self.assertEqual(len(result[1]), 9)
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_split_with_complex_parenthesis_structure(self):
        tokens = Tokenizer().split("What the heck? (A) First things here.")
        sep = 4
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep], tokens[sep:]], result)

    def test_split_with_a_simple_parenthesis_structure(self):
        tokens = Tokenizer().split(
            "And another sentence on the same line. "
            "(How about a sentence in parenthesis?) "
            'Or a sentence with "a quote!"'
        )
        sep1 = 8
        sep2 = 17
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens[:sep1], tokens[sep1:sep2], tokens[sep2:]], result)

    def test_no_split_with_simple_inner_bracketed_text(self):
        tokens = Tokenizer().split("Specimens (n = 32) were sent for 16S rRNA PCR.")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_no_split_on_strange_text(self):
        tokens = Tokenizer().split(
            "Four patients (67%) with an average response of 3.3 mos. (range 6 wks. to 12 mos.)"
        )
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_no_split_on_strange_text2(self):
        tokens = Tokenizer().split(
            "Packed cells (PRBC) for less than 20,000 thousand/micro.L, repsectively."
        )
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)

    def test_no_split_on_strange_text3(self):
        tokens = Tokenizer().split("This is Company Wag.B.H., truly.")
        result = segmenter.split(iter(tokens))
        self.assertEqual([tokens], result)


class TestPreprocess(TestCase):
    def test_preprocess_with_offsets(self):
        text = " ab\n\u00a0 \n cd- \n ef \n\n g \n \n"
        result = segmenter.preprocess_with_offsets(text)
        self.assertListEqual(
            [(0, " ab"), (7, " cd- \n ef "), (19, " g "), (25, "")], result
        )

    def test_preprocess(self):
        text = " ab\n\u00a0 \n  cd- \n ef \n\n g \n \n"
        result = segmenter.preprocess(text)
        self.assertListEqual([" ab", "  cdef ", " g ", ""], result)


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
                    if (
                        token.value and token.value != "tincidunt"
                    ):  # tin-cidunt linebreak!
                        new_offset = DOCUMENT.find(token.value, offset)
                        self.assertNotEqual(
                            new_offset, -1, repr(token) + " at %d" % offset
                        )
                        offset = new_offset + len(token.value)
