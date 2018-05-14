import glob
import os
import pathlib
import subprocess

import pandas as pd
import pickle

from src.document import Document


def load_corpus(corpus_path):

    corpus = []

    # Load all review files inside de corpus folder
    for filename in glob.glob(os.path.join(corpus_path, '*.txt')):

        review_year = int(os.path.basename(filename)[7:11])
        review_code = int(os.path.basename(filename)[12:13])
        review_file = open(filename, 'r')
        review_data = review_file.read().replace('\n', '.')
        review_file.close()

        # Create a list of Document objects containing each review
        review = Document(review_data, review_year)
        corpus.append(review)

    return(corpus)


def load_pickle_object(filename, class_name, class_args):
    """
    Load any class object stored with Pickle.
    Create and store a new instance in case it doesn't exist.

    Parameters
    ----------
    filename : String
        File storing a Pickle object
    class_name : Class type definition
        Class definition corresponding to the object being loaded
    class_args: List
        List of arguments being passed to the class constructor

    Returns
    -------
    loaded_object: Instance of type 'class_name'
    """

    try:
        with open(filename, 'rb') as f:
            loaded_object = pickle.load(f)

    except (OSError, IOError) as e:
        loaded_object = class_name(*class_args)
        with open(filename, 'wb') as f:
            pickle.dump(loaded_object, f)

    return(loaded_object)


def normalize_corpus(input_folder, output_folder):
    """
    Note
    ----
    This function requires the UGCNormal normalizer to be on the parent directory.
    A fork of the project, including minor adjusts, can be obtained at:
    https://github.com/guimaraescca/UGCNormal
    """

    subprocess.call(['../UGCNormal/ugc_norm.sh', input_folder, output_folder])


def sheet_to_file(sheet_file):

    # Load sheet file as Dataframe
    df_piloto = pd.read_excel(sheet_file, index_col=0, sheet_name=0, engine=None)

    # Create corpus year folders
    for i in range(0, 5):
        folder_name = '../data/processed/corpus/original/{}'.format(2013 + i)
        pathlib.Path(folder_name).mkdir(parents=True, exist_ok=True)

    # For every review in the Dataframe create a new file
    for i, row in enumerate(df_piloto.itertuples(index=True)):
        filename = '../data/processed/corpus/original/{}/review-{}-{}.txt'.format(row[0], row[0], i % 10)
        with open(filename, 'w') as review_file:
            review_file.write(row[5])


def update_polarity_count(df_corpus, review_polarities, year):

    # For each aspect and it's polarity value in the given review
    for aspect, polarity in review_polarities.items():

        # Obtain indexes that match the given 'aspect' and 'year'
        df_id = df_corpus[(df_corpus.Aspect == aspect) & (df_corpus.Year == year)].index.tolist()

        # Insert new occurrence if nothing was found
        if df_id == []:
            new_row = pd.DataFrame([[aspect, year, 0, 0]], columns=df_corpus.columns)
            df_corpus = df_corpus.append(new_row, ignore_index=True)

            df_id = df_corpus[(df_corpus.Aspect == aspect) & (df_corpus.Year == year)].index.tolist()

        # Update polarity on the corpus DataFrame
        if polarity >= 0:
            df_corpus.at[df_id[0], 'Positive'] += 1
        else:
            df_corpus.at[df_id[0], 'Negative'] += 1

    return(df_corpus)
