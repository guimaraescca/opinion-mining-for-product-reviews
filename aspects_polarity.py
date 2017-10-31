# Standart libraries
import string

# Third-party libraries
import nltk
import rdflib
from rdflib.namespace import RDF, OWL

# Download data for the tokenization process
# nltk.download('punkt')

# Context words for polarity change
negation = ['jamais', 'nada', 'nem', 'nenhum', 'ninguém', 'nunca', 'não',
            'tampouco']
amplifier = ['mais', 'muito', 'demais', 'completamente', 'absolutamente',
             'totalmente', 'definitivamente', 'extremamente', 'frequentemente',
             'bastante']
downtoner = ['pouco', 'quase', 'menos', 'apenas']


class LIWC:
    """
    LIWC dictionary and data class.
    """

    def __init__(self, filename, remove_asterisk=True):
        """Construct LIWC object and initilize the sentiment word dictionary."""

        self.file = open(filename, 'r', encoding='latin-1')
        self.data = self.file.readlines()
        self.dict = dict()

        # Iterate across the LIWC data
        for line in self.data:
            line_words = line.rstrip('\r\n').split()
            word = line_words[0]
            categories = line_words[1:]

            # Remove asterisk notation from word if required
            if remove_asterisk and word[-1] == '*':
                word = word[:-1]

            # Add word to it's corresponding emotion set
            if '126' in categories:
                # Store word as positive emotion
                self.dict[word] = +1

            elif '127' in categories:
                # Store word as an negative emotion
                self.dict[word] = -1

    def get_sentiment(self, word):
        """
        Search a given word on the LIWC dictionary and return the polarity
        associated to it ('-1'/'+1'), otherwise return None.
        """

        # List of word derivations to search for on dictionary
        word_derivations = [word]

        # Add to the list derivations of 'word' removing it's last letters
        if len(word) > 2:
            word_derivations.append(word[:-1])
        if len(word) > 3:
            word_derivations.append(word[:-2])

        # Query the word derivations
        for term in word_derivations:
            polarity = self.dict.get(term)

            # Polarity found (-1 or +1)
            if polarity is not None:
                return(polarity)

        # No polarity value found on the dictionary
        return(None)


class Ontology:
    """
    OWL Ontology class.
    """

    def __init__(self, filename):
        """Construct an Ontology object and create the corresponding RDFLIB graph."""
        self.g = rdflib.Graph()
        self.g.load(filename)

    def search(self, search_term):
        """
        Search for an aspect or aspect's class that corresponds to the given term.
        Returns the aspect or aspect's class in case of success. Otherwise, return 'None'.
        """

        search_term = search_term.lower()

        # Search for every relation 'is a type of' between aspects and classes
        for b in self.g.subject_objects(RDF.type):

            # Check if the subject is a class
            is_class = False
            if (b[1] == OWL.Class): is_class = True

            # Discard some nonrelevant objects
            if b[1] != OWL.NamedIndividual and b[1] != OWL.Ontology:

                # Extract subject as a lowercase string
                sub = self.g.label(b[0]).toPython().lower()

                # Select results that match the search
                if sub == search_term:
                    if is_class:
                        return(sub)
                    else:
                        obj = self.g.label(b[1]).toPython().lower()
                        return(obj)

        return(None)


class Document:
    """
    Document class containing all data about an opinion text.
    """

    def __init__(self, text):

        self.text = text
        self.words = nltk.word_tokenize(text.lower())
        self.word_tag = []

        # Dictionary of aspects occurrences
        self.aspect_pos = dict()

        # Dictionary of aspects polarity
        self.aspect_polarity = dict()

        # Dictionary of informations about the aspect context
        self.aspect_context = dict()

    def print_data(self):
        """
        Show on screen each document word and it's corresponding tag.
        Used for debbuging the tagging method.
        '"""

        print(f'[ #] [Word]          [Tag]')
        for i, word in enumerate(self.words):
            print(f'[{i:{2}}] {word:{15}} {self.word_tag[i]}')

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
                # Search on the ontology for a matching aspect
                aspect = ontology.search(word)

                # Check if word is an aspect
                if aspect is not None:
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

    def compute_sentence(self):
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
                self.aspect_polarity[aspect] = 0

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

    def print_aspect_data(self):
        """
        Show polarities associated to each aspect in review, based on context
        """

        print(f'[Aspect] \t[Overall polarity]')
        for key, item in self.aspect_polarity.items():
            print(f'\'{key}\' \t{item}')

    def print_aspect_context(self):
        """
        Show information about known aspect, respective context range, and associated
        sentiment words with it's positions.
        """

        for pos, info in self.aspect_context.items():
            print(f'\nFound ({self.aspect_pos.get(pos)}) as ({self.words[pos]}). Context {info[0]}')
            if len(info) == 1:
                print('   No sentiment word found.')
            else:
                print(f'   [Aspect]\t[Position]')
                for s_pos in info[1:]:
                    print(f'   {self.words[s_pos]}  \t{s_pos}')


def main():

    # Create a LIWC dictionary
    liwc = LIWC(filename='liwc_dictionaries/LIWC2007_Portugues_win.dic')

    # Load ontology of aspects
    ontology = Ontology('ontologies/smartphone_aspects.owl')

    # Load corpus data
    text = 'Ótimo celular, desempenho e design espetaculares, superou minhas expectativas. Outra coisa que se destaca bastante é a bateria, com uma grande duração. Os fones que acompanham o celular são provavelmente os melhores que eu já utilizei, com uma qualidade sonora e um isolamento fenomenais. A samsung realmente inovou neste celular'
    text2 = 'Adorei o celular, design muito bonito e moderno. Apesar disso, a bateria não dura muito.'

    # Create an Document object to contain all info about the review
    review = Document(text2)

    print('\n>>> Review:\n', review.text)
    print('\n>>> Word tokenization:\n', review.words)

    # Tag the review data using the dictionaries
    review.tag_words(liwc, ontology)

    # Parse the review to compute aspects polarities
    review.compute_sentence()

    # Show relevant data about the review

    # Show the review words and the respective tags
    review.print_data()

    # Relevant information obtained from each aspect context
    review.print_aspect_context()

    # Polarities associated to each aspect in review (based on context)
    review.print_aspect_data()


if __name__ == '__main__':
    main()
