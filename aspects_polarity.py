# Standart libraries
import re

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


def init_sets(liwc):
    """
    Search on LIWC for words in the positive and negative emotions categories
    and group them in the respective set.
    """

    # Iterate across the LIWC data
    for line in liwc:
        line_words = line.rstrip('\r\n').split()
        word = line_words[0]
        categories = line_words[1:]

        # Add word to it's corresponding emotion set
        if '126' in categories:
            posemo_set.add(word)
        elif '127' in categories:
            negemo_set.add(word)


def search_sets(word):
    """Search sentiment sets for the occurrence of a sentiment word."""

    # Check for positive or negative emotions
    if search_regex(word, posemo_set):
        return(1)
    elif search_regex(word, negemo_set):
        return(-1)

    # No class correspond to a sentiment word
    else:
        return(False)


def search_regex(word, sentiment_set):
    """Search using a regex for the occurrence of 'word' in the sentiment set"""

    # Concatenate word with regex
    pattern = r'^' + re.escape(word) + r'[*]?\b'

    # Look for the pattern on the sets
    for sent_word in sentiment_set:
        match = re.search(fr'{pattern}', sent_word)
        if match:
            return True

    return False


def word_tagger(ontology, review):
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
                    polarity = search_sets(word)

                    # Word is not a sentiment word
                    if polarity is False:
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

    # Load the LIWC dictionary
    liwc_path = 'liwc_dictionaries/LIWC2007_Portugues_win.dic'
    liwc_file = open(liwc_path, 'r', encoding='latin-1')
    liwc = liwc_file.readlines()

    # Initialize sentiment sets
    init_sets(liwc)

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
    document_markup = word_tagger(ontology, document_data)

    # Create a dictionary fo polarties aspects
    # print('\n[Compute the polarities]')
    # compute_polarities(document_markup, 4)

    print_review_data(document_data, document_markup)


if __name__ == '__main__':
    main()
