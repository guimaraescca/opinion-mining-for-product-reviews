# Third-party libraries
import nltk
# nltk.download('punkt') # Download data for the tokenization process


# Global data structures
posemo_set = set()          # Set of positive sentiment words
negemo_set = set()          # Set of negative sentiment words

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
        associated to it (-1/+1), otherwise return None.
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


def pre_processing(document, remove_punctuation=False):
    """
    Convert words to lower case, tokenize document into a list of words for each
    sentence.
    """

    # Convert to lower case
    document = document.lower()

    # Tokenize document in sentences using Punkt for BP (Brazilian Portuguese)
    stok = nltk.data.load('tokenizers/punkt/portuguese.pickle')
    document_sentences = stok.tokenize(document)

    # Tokenize sentences in words
    document_data = []
    for sentence in document_sentences:
        document_data.append(nltk.word_tokenize(sentence))

    return(document_data)


def search_ontology(ontology, word):
    """Search ontology for the occurrence of an aspect"""
    for i in ontology:
        if i == word:
            return True
    return False


def word_tagger(liwc, ontology, review):
    """
    Identify aspects, sentiment and context changing words for a given document.
    """

    document_markup = []

    for sentence in review:
        sentence_markup = []

        for pos, word in enumerate(sentence):

            # Check if word is context changing one (negation, amplifier or downtoner)
            if word in negation:
                sentence_markup.append('negation')

            elif word in amplifier:
                sentence_markup.append('amplifier')

            elif word in downtoner:
                sentence_markup.append('downtoner')

            else:

                # Search on the ontology for a matching aspect
                asp_check = search_ontology(ontology, word)

                # Check if word is an aspect
                if asp_check is True:
                    aspect_pos[pos] = word              # Mark the aspect position
                    sentence_markup.append('aspect')

                # Check if word is a sentiment word
                else:

                    # Search on LIWC for a polarity conotation
                    polarity = liwc.get_sentiment(word)

                    # Word is not a sentiment word
                    if polarity is None:
                        sentence_markup.append('')

                    # Attribute polarity value to the position
                    else:
                        sentence_markup.append(polarity)

        # Add the tagged sentence to the document list
        document_markup.append(sentence_markup)

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


def print_review_data(document_data, document_markup):
    """
        Print word's tag for each sentence in review. Used for debbuging the
    'word_tagger()' method.
    '"""

    for i, sentence in enumerate(document_data):
        print(f'\nSentence [{i}]: \n{sentence}')
        print(f'[ #] [Word]          [Tag]')
        for j, word in enumerate(sentence):
            print(f'[{j:{2}}] {word:{15}} {document_markup[i][j]}')


def main():

    # Create a LIWC dictionary
    liwc = LIWC(filename='liwc_dictionaries/LIWC2007_Portugues_win.dic')

    # Load data corpus and ontology
    review = 'Ótimo celular, desempenho e design espetaculares, superou minhas expectativas. Outra coisa que se destaca bastante é a bateria, com uma grande duração. Os fones que acompanham o celular são provavelmente os melhores que eu já utilizei, com uma qualidade sonora e um isolamento fenomenais. A samsung realmente inovou neste celular.'
    ontology = ['celular', 'desempenho', 'design', 'bateria', 'fones']

    # Pre-process the reviews
    print('[Pre-processing]')
    document_data = pre_processing(review)

    print('\n>>> Review:\n', review)
    print('\n>>> Tokenization of sentences and words:')
    for i, sentence in enumerate(document_data):
        print(f'[{i:{2}}] {sentence}')

    # Analysis
    print('\n[Parsing the review]')
    document_markup = word_tagger(liwc, ontology, document_data)

    # Create a dictionary fo polarties aspects
    # print('\n[Compute the polarities]')
    # compute_polarities(document_markup, 4)

    print_review_data(document_data, document_markup)


if __name__ == '__main__':
    main()
