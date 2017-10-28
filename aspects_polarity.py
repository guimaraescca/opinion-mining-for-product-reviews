import string

# Third-party libraries
import nltk
import rdflib
from rdflib.namespace import RDF, OWL

# Download data for the tokenization process
# nltk.download('punkt')

# Global data structures
aspect_pos = dict()         # Dictionary of aspects position
aspect_polarity = dict()    # Dictionary of aspects polarity


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

        # No polarity value was found on the dictionary
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


def word_tagger(liwc, ontology, review):
    """
    Identify aspects, sentiment and context changing words for a given document.
    """

    document_markup = []

    for pos, word in enumerate(review):

        # Check if word is context changing one (negation, amplifier or downtoner)
        if word in negation:
            document_markup.append('negation')
        elif word in amplifier:
            document_markup.append('amplifier')
        elif word in downtoner:
            document_markup.append('downtoner')

        else:
            # Search on the ontology for a matching aspect
            asp_check = ontology.search(word)

            # Check if word is an aspect
            if asp_check is not None:
                aspect_pos[pos] = asp_check         # Mark the aspect position
                document_markup.append('aspect')

            # Check if word is a sentiment word
            else:
                # Search on LIWC for a polarity conotation
                polarity = liwc.get_sentiment(word)

                # Word is not a sentiment word
                if polarity is None:
                    document_markup.append('')

                # Attribute polarity value to the position
                else:
                    document_markup.append(polarity)

    return(document_markup)


def get_polarity_inrange(document_markup, pos, word_range):
    """Sum the polarity values surrounding the aspect for the given position."""

    polarity = 0
    end = len(document_markup) - 1

    # Set start and end positions to scan polarities in the review
    start_pos = pos - word_range if pos >= word_range else 0
    end_pos = pos + word_range if pos + word_range <= end else end

    for i in range(start_pos, end_pos + 1):
        polarity += document_markup[i]

    return(polarity)


def compute_polarities(document_markup, word_range=4):
    """"Compute the polarity values for each aspect identified in a review.

    document_markup: list
        List that mark up polarities and aspect for a given list of words from a review
    word_range: int
        Number of words to look for polarities around a found aspect.
    """

    # Compute the polarity value for each aspect
    for pos, aspect in aspect_pos.items():
        polarity = get_polarity_inrange(document_markup, pos, word_range)

        # Check if the aspect had occur once
        if aspect in aspect_polarity:
            aspect_polarity[aspect] += polarity

        # Otherwise just attribute the value to the aspect
        else:
            aspect_polarity[aspect] = polarity


def print_review_data(review_data, document_markup):
    """
    Print word's tag for each sentence in review. Used for debbuging the
    'word_tagger()' method.
    '"""

    print(f'[ #] [Word]          [Tag]')
    for i, word in enumerate(review_data):
        print(f'[{i:{2}}] {word:{15}} {document_markup[i]}')


def compute_sentence(review_data, document_markup):

    punctuation = list(string.punctuation)

    # For each aspect position, define the sentence range
    for pos in aspect_pos.keys():
        sentiment_pos = []
        start = pos
        end = pos

        # Set sentence start
        while(start > 0 and review_data[start - 1] not in punctuation):
            start -= 1
            if document_markup[start] == -1 or document_markup[start] == 1:
                # print('start: ', review_data[start])
                sentiment_pos.append(start)

        # Set sentence end
        while(end < len(review_data) - 1 and review_data[end + 1] not in punctuation):
            end += 1
            if document_markup[end] == -1 or document_markup[end] == 1:
                # print('end:', document_markup[end])
                sentiment_pos.append(end)

        print(f'\nSentence for \'{aspect_pos.get(pos)}\': [{start},{end}]')
        print(f'Sentiment words ({len(sentiment_pos)}):')
        for s_pos in sentiment_pos:
            print(f'\'{review_data[s_pos]}\' at {s_pos}')

        for s_pos in sentiment_pos:
            polarity = document_markup[s_pos]



def main():

    # Create a LIWC dictionary
    liwc = LIWC(filename='liwc_dictionaries/LIWC2007_Portugues_win.dic')

    # Load ontology of aspects
    ontology = Ontology('ontologies/smartphone_aspects.owl')

    # Load corpus data
    review = 'Ótimo celular, desempenho e design espetaculares, superou minhas expectativas. Outra coisa que se destaca bastante é a bateria, com uma grande duração. Os fones que acompanham o celular são provavelmente os melhores que eu já utilizei, com uma qualidade sonora e um isolamento fenomenais. A samsung realmente inovou neste celular'

    # Pre-process the reviews
    print('[Pre-processing]')
    review_data = nltk.word_tokenize(review.lower())

    print('\n>>> Review:\n', review)
    print('\n>>> Word tokenization:\n', review_data)

    # Analysis
    print('\n[Parsing the review]')
    document_markup = word_tagger(liwc, ontology, review_data)

    # Create a dictionary for polarties aspects
    # print('\n[Compute the polarities]')
    # compute_polarities(document_markup, 4)

    # print_review_data(review_data, document_markup)

    compute_sentence(review_data, document_markup)
    print(aspect_pos)


if __name__ == '__main__':
    main()
