# Standart libraries
import os
import glob
import subprocess

# Third-party libraries
import pandas as pd
import numpy as np

# Local files
from liwc import LIWC
from ontology import Ontology
from document import Document

corpus_polarity = dict()
df_corpus_pol = pd.DataFrame()


def compute_total(review_polarities):

    for aspect, polarity in review_polarities.items():

        if polarity >= 0:
            corpus_polarity[aspect] = corpus_polarity.get(aspect, np.zeros((1, 2))) + np.array((1, 0))
        else:
            corpus_polarity[aspect] = corpus_polarity.get(aspect, np.zeros((1, 2))) + np.array((0, 1))


def main():

    # Create a LIWC dictionary
    liwc = LIWC(filename='liwc_dictionaries/LIWC2007_Portugues_win.dic')

    # Load ontology of aspects
    ontology = Ontology('ontologies/smartphone_aspects.owl')

    # Apply the UGCNormal Normalizer to the corpus
    # subprocess.call(['UGCNormal/ugc_norm.sh', 'corpus/', 'corpus-normalized/'])

    # Create an Document object to contain all info about the review
    filename = 'corpus-normalized/tok/checked/siglas/internetes/nomes/review-2017-1.txt'

    review_file = open(filename, 'r')
    review_data = review_file.read().replace('\n', ' . ')
    review_file.close()

    # Load corpus data
    text = 'Ótimo celular, desempenho e design espetaculares, superou minhas expectativas. Outra coisa que se destaca bastante é a bateria, com uma grande duração. Os fones que acompanham o celular são provavelmente os melhores que eu já utilizei, com uma qualidade sonora e um isolamento fenomenais. A samsung realmente inovou neste celular'
    text2 = 'Adorei o celular, design muito bonito e moderno. Apesar disso, a bateria não dura muito.'

    review_data = text2

    review = Document(review_data, 2000)

    print('\n>>> Review:\n', review.text)
    print('\n>>> Word tokenization:\n', review.words)

    # Tag the review data using the dictionaries
    review.tag_words(liwc, ontology)

    # Parse the review to compute aspects polarities
    review.compute_polarity()

    # Show relevant data about the review

    # Show the review words and the respective tags
    review.print_data()

    # Relevant information obtained from each aspect context
    review.print_aspect_context()

    # Polarities associated to each aspect in review (based on context)
    review.print_aspect_data()


if __name__ == '__main__':
    main()
