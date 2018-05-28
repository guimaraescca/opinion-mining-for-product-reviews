# Standart libraries
import os

# Third-party libraries
import pandas as pd

# Local files
import utils
from liwc import LIWC
from ontology import Ontology

PROJ_ROOT = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))


def main():

    # Load LIWC dictionary
    liwc = utils.load_pickle_object(filename=os.path.join(PROJ_ROOT, 'data/interim/liwc-object.pickle'),
                                    class_name=LIWC,
                                    class_args=[os.path.join(PROJ_ROOT, 'data/external/liwc/LIWC2007_Portugues_win.dic')])

    # Load ontology of aspects
    ontology = Ontology(os.path.join(PROJ_ROOT, 'data/external/ontologies/smartphone_aspects.owl'))

    # Apply the UGCNormal Normalizer to the corpus
#     utils.sheet_to_file(os.path.join(PROJ_ROOT, 'data/raw/pilot-study-reviews.xlsx'))
#     utils.normalize_corpus(os.path.join(PROJ_ROOT, 'data/processed/corpus/original/'), os.path.join(PROJ_ROOT, 'data/processed/corpus/normalized/'))

    # Read the corpus data
    corpus = utils.load_corpus(os.path.join(PROJ_ROOT, 'data/processed/corpus/normalized/tok/checked/siglas/internetes/nomes/'))

    # Create a Pandas DataFrame to hold the polarity count data
    df_corpus = pd.DataFrame(columns=['Aspect', 'Year', 'Positive', 'Negative'])

    # Corpus analysis
    for i, review in enumerate(corpus):
        if i >= 2:
            return
        print(f'\nReview #{i}\n {review.text}.')

        # Tag the review data using the dictionaries
        review.tag_words(liwc, ontology)

        # Parse the review to compute aspects polarities
        review.compute_polarity()

        # Show polarities associated to each aspect in review (based on context)
        review.print_aspect_data()
        review.print_aspect_context()

        # Use review data to update the corpus count
        df_corpus = utils.update_polarity_count(df_corpus, review.aspect_polarity, review.date)

    # Compute the total number of occurrences on the DataFrame
    df_corpus['Occurrences'] = df_corpus[['Positive', 'Negative']].sum(axis=1)

    # Create new DataFrame couning aspect's overall occurrences
    df_overall = df_corpus.groupby(['Aspect'])[['Occurrences']].sum().sort_values('Occurrences', ascending=False)

    # Normalize the positive and negative count
    df_corpus[['Positive', 'Negative']] = 100 * df_corpus[['Positive', 'Negative']].div(df_corpus['Occurrences'], axis=0)

    # Set the aspect's column as the index
    # df_corpus_pol = df_corpus_pol.set_index('Aspect')

    return(df_corpus, df_overall)


if __name__ == '__main__':
    df_corpus, df_overall = main()
