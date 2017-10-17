# Standart libraries
import string

# Third-party libraries
import LIWCtools.LIWCtools as lt
import nltk             # word_tokenize()

# Download data for the tokenization process
# nltk.download('punkt')

aspect_pos = dict()         # Dictionary of aspects position
aspect_polarity = dict()    # Dictionary of aspects polarity

# Context words for polarity change
negation = ['jamais', 'nada', 'nem', 'nenhum', 'ninguém', 'nunca', 'não',
            'tampouco']
amplifier = ['mais', 'muito', 'demais', 'completamente', 'absolutamente',
             'totalmente', 'definitivamente', 'extremamente', 'frequentemente',
             'bastante']
downtoner = ['pouco', 'quase', 'menos', 'apenas']


def pre_processing(document):
    """Tokenize and eliminate punctuation for a given document"""

    # Convert to lower case
    document = document.lower()

    # Tokenize the document
    document_tokens = nltk.word_tokenize(document)

    # Remove punctuation - i.e. !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    document_words = []
    for word in document_tokens:

        if word not in string.punctuation:
            document_words.append(word)

    return(document_words)


def search_ontology(ontology, word):
    """Search ontology for the occurrence of an aspect"""
    for i in ontology:
        if i == word:
            return True
    return False


def search_liwc(LIWCDict, word):
    """Search a LIWC dictionary for the occurrence of a sentiment word"""

    # Query the LIWC for the respective classes
    classes_found = LIWCDict.LDictCountString(word)

    # Check for positive or negative emotions
    for cl in classes_found:
        if cl == 'posemo':
            return(1)
        elif cl == 'negemo':
            return(-1)

    # No class correspond to a sentiment word
    return(False)


def word_tagger(LIWCDict, ontology, review, flag_print=False):
    """
        Identify aspects, sentiment and context changing words for a given
    document.
    """

    document_markup = []

    for pos, word in enumerate(review):

        # Check if word is an aspect
        asp_check = search_ontology(ontology, word)

        # If the search return a valid position
        if asp_check is True:
            if flag_print is True:
                print(f'Aspect:\t\t {word}')

            aspect_pos[pos] = word
            document_markup.append(0)
            pos += 1

        # Check if word is a sentiment word
        else:
            polarity = search_liwc(LIWCDict, word)

            # Current word is not a sentiment word
            if polarity is False:
                document_markup.append(0)
                pos += 1

            # Attribute the respective polarity value to the position
            else:
                if flag_print is True:
                    print(f'Sent. word:\t {word} (pol={polarity})')
                document_markup.append(polarity)
                pos += 1

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


def main():

    # Load the LIWC dictionary
    liwc_path = 'liwc_dictionaries/LIWC2007_Portugues_win.dic'
    LIWCDict = lt.LDict(liwc_path, encoding='latin-1')

    # Load sentence tokenizer
    stok = nltk.data.load('tokenizers/punkt/portuguese.pickle')

    # Load data
    review = 'Ótimo celular, desempenho e design espetaculares, superou minhas expectativas. Outra coisa que se destaca bastante é a bateria, com uma grande duração. Os fones que acompanham o celular são provavelmente os melhores que eu já utilizei, com uma qualidade sonora e um isolamento fenomenais. A samsung realmente inovou neste celular.'
    ontology = ['celular', 'desempenho', 'design', 'bateria', 'fones']

    # Pre-process the reviews
    print('\n[Pre-processing]')
    review_words = pre_processing(review)

    print('>>> Review:\n\t', review)
    print('>>> Tokenization:\n\t ', review_words)

    # Start analysis
    print('\n[Parsing the review]')
    document_markup = word_tagger(LIWCDict, ontology, review_words, False)

    # Create a dictionary fo polarties aspects
    print('\n[Compute the polarities]')
    compute_polarities(document_markup, 4)

    print(aspect_polarity)


if __name__ == '__main__':
    main()
