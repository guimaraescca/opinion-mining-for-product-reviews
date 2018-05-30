"""
Class and functions to analyse data contained in opinion documents.
"""

# Standart libraries
import string

# Third-party libraries
import nltk
from nltk.tokenize import MWETokenizer

# Download data for the tokenization process
nltk.download('punkt')

# Context words for polarity change
negation = set(['jamais', 'nada', 'nem', 'nenhum', 'ninguém', 'nunca', 'não',
                'tampouco'])
amplifier = set(['mais', 'muito', 'demais', 'completamente', 'absolutamente',
                 'totalmente', 'definitivamente', 'extremamente',
                 'frequentemente', 'bastante'])
downtoner = set(['pouco', 'quase', 'menos', 'apenas'])


class Document:
    """
    Document class containing all data about an opinion text.
    """

    def __init__(self, text, date, mwaspects):

        self.text = text
        self.date = date
        tokens = nltk.word_tokenize(text.lower())
        mwtokenizer = MWETokenizer(mwaspects, separator=' ')
        self.words = mwtokenizer.tokenize(tokens)
        self.word_tag = []

        # Dictionary of aspects occurrences
        self.aspect_pos = dict()

        # Dictionary of aspects polarity
        self.aspect_polarity = dict()

        # Dictionary of informations about the aspect context
        self.aspect_context = dict()

    def tag_words(self, liwc, ontology):
        """
        Identify aspects, sentiment and context changing words for a given document.
        """

        for pos, word in enumerate(self.words):

            # Check if word is context changing one (negation, amplifier or downtoner)
            if word in negation:
                self.word_tag.append('negation')
            elif word in amplifier:
                self.word_tag.append('amplifier')
            elif word in downtoner:
                self.word_tag.append('downtoner')

            else:
                # Check if word is an aspect
                if word in ontology:
                    aspect = ontology[word]

                    # Mark the aspect occurrence position
                    self.aspect_pos[pos] = aspect
                    self.word_tag.append('aspect')

                # Check if word is a sentiment word
                else:
                    # Search on LIWC for a polarity conotation
                    polarity = liwc.get_sentiment(word)

                    # Word is not a sentiment word
                    if polarity is None:
                        self.word_tag.append('')

                    # Attribute polarity value to the position
                    else:
                        self.word_tag.append(polarity)

    def compute_polarity(self):
        """
        Atribute polarity to aspects based on surround sentiment words context.

        Calculate the sentence limits in which the located aspects are, identify
        related sentiment words and atribute polarity value to the aspects based
        on the sentiments context.
        """

        punctuation = list(string.punctuation)

        # For each aspect position, define the sentence range
        for pos in self.aspect_pos.keys():
            sentiment_pos = []
            start = pos
            end = pos

            # Set sentence start
            while(start > 0 and self.words[start - 1] not in punctuation):
                start -= 1
                if self.word_tag[start] == -1 or self.word_tag[start] == 1:
                    sentiment_pos.append(start)

            # Set sentence end
            while(end < len(self.words) - 1 and self.words[end + 1] not in punctuation):
                end += 1
                if self.word_tag[end] == -1 or self.word_tag[end] == 1:
                    sentiment_pos.append(end)

            # Store aspect sentence range
            self.aspect_context.setdefault(pos, []).append((start, end))

            # Get aspect's name
            aspect = self.aspect_pos.get(pos)

            # Compute the polarity for each sentiment word around the aspect
            for s_pos in sentiment_pos:

                # Store sentiment word
                self.aspect_context.setdefault(pos, []).append(s_pos)

                # Compute the polarity for the sentiment word context
                context_polarity = self._get_context_polarity(s_pos)

                # Sum the context polarity with any previous one for the current aspect
                self.aspect_polarity[aspect] = self.aspect_polarity.get(aspect, 0) + context_polarity

            # In case there's no sentiment word around the aspect
            if len(sentiment_pos) == 0:
                self.aspect_polarity[aspect] = self.aspect_polarity.get(aspect, 0) + 0

    def _get_context_polarity(self, pos, word_range=4):
        """
        Compute the context information around a sentiment word, given it's
        position 'pos' and a range 'word_range' to lookup for.

        Return the sentiment word polarity based on the given word range.
        """
        punctuation = list(string.punctuation)

        reached_start = False
        reached_end = False

        f_amplifier = False
        f_downtoner = False
        f_negation = False

        # For each word inside 'word_range' around the sentiment
        for i in range(1, word_range + 1):

            # Mark valid
            if pos - i >= 0 and pos + i < len(self.words):

                # Stop search if a punctuation mark found
                if not reached_start and self.words[pos - i] in punctuation:
                    reached_start = True
                if not reached_end and self.words[pos + i] in punctuation:
                    reached_end = True

                # Otherwise include word in context
                if not reached_start:
                    if self.word_tag[pos - i] == 'amplifier': f_amplifier = True
                    elif self.word_tag[pos - i] == 'downtoner': f_downtoner = True
                    elif self.word_tag[pos - i] == 'negation': f_negation = True
                if not reached_end:
                    if self.word_tag[pos + i] == 'amplifier': f_amplifier = True
                    elif self.word_tag[pos + i] == 'downtoner': f_downtoner = True
                    elif self.word_tag[pos + i] == 'negation': f_negation = True

        # Get the sentiment word polarity based on context
        polarity = self._get_sentiment_polarity(pos, f_amplifier, f_downtoner, f_negation)

        return(polarity)

    def _get_sentiment_polarity(self, pos, f_amplifier, f_downtoner, f_negation):
        """
        Return the sentiment word polarity given the word position 'pos' and
        information about the context.
        """

        # Set a priori polarity
        polarity = self.word_tag[pos]

        # Algorith to calculate the overall sentiment
        if f_amplifier:
            if f_negation:
                polarity = polarity / 3
            else:
                polarity = polarity * 3
        elif f_downtoner:
            if f_negation:
                polarity = polarity * 3
            else:
                polarity = polarity / 3
        elif f_negation:
            polarity = -1 * polarity

        return(polarity)

    def print_data(self):
        """
        Show on screen each document word and it's corresponding tag.
        Used for debbuging the tagging method.
        '"""

        print(f'\n[ #] [Word]          [Tag]')
        for i, word in enumerate(self.words):
            print(f'[{i:{2}}] {word:{15}} {self.word_tag[i]}')

    def print_aspect_data(self):
        """
        Show polarities associated to each aspect in review, based on context
        """

        print(f'\n[Aspect]               [Overall polarity]')
        for key, item in self.aspect_polarity.items():
            print(f'{key:{22}} {item}')

    def print_aspect_context(self):
        """
        Show information about known aspect, respective context range, and associated
        sentiment words with it's positions.
        """

        for pos, info in self.aspect_context.items():
            print(f'\nFound ({self.aspect_pos.get(pos)}) as ({self.words[pos]}). Context {info[0]}')
            if len(info) == 1:
                print('   Nothing found.')
            else:
                print(f'   [Aspect]            [Polarity] [Position]')
                for s_pos in info[1:]:
                    print(f'   {self.words[s_pos]:{15}} {self.word_tag[s_pos]:{5}} {s_pos:{12}}')
