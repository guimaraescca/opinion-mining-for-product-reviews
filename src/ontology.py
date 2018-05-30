"""
Class and functions to query terms from OWL Ontologies.
"""

# Third party libraries
import pandas as pd
import rdflib
import rdflib.plugins.sparql as sparql
from rdflib.namespace import RDF, RDFS, OWL


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
        Search for an aspect that corresponds to the given term.
        Returns the aspect's class in case of success. Otherwise, returns 'None'.
        """

        search_term = search_term.lower()

        # Especifies the query syntax
        query = sparql.prepareQuery("""
                    SELECT DISTINCT ?individualLabel ?classLabel
                    WHERE {
                        ?y rdf:type owl:Class .
                        ?y rdfs:label ?classLabel .
                        OPTIONAL {
                            ?x rdf:type ?y .
                            ?x rdfs:label ?individualLabel .
                        }
                        FILTER( REGEX(str(?individualLabel), "^%s([_]|$)|([_]|^)%s$", "i") ||
                                REGEX(str(?classLabel), "^%s([_]|$)|([_]|^)%s$", "i"))
                    }
                    ORDER BY ASC(?classLabel)""" % (search_term, search_term, search_term, search_term),
                    initNs={'rdf': RDF, 'rdfs': RDFS, 'owl': OWL})

        # Perform the query through the ontology
        query_result = self.g.query(query, DEBUG=True)

        # Transform the query results to a Pandas DataFrame format
        data = []
        for row in query_result:
            data_row = []
            for x in row:
                if x is not None:
                    x = x.toPython()
                data_row.append(x)
            data.append(data_row)

        df = pd.DataFrame(data, columns=['individualLabel', 'classLabel'])

        # Retrives the first class listed on the DataFrame, in case it exists
        try:
            result_class = df.loc[0, 'classLabel']
        except KeyError:
            result_class = None

        return(result_class)


def ontology_to_dict(filename):
    """
    Create a dictionary of aspects based on a given ontology.

    The returned dict has keys representing aspects and values corresponding to the closest
    cluster on the ontology.
    """

    g = rdflib.Graph()
    g.load(filename)

    query_classes = sparql.prepareQuery("""
            SELECT DISTINCT ?classLabel
            WHERE {
                ?y rdf:type owl:Class .
                ?y rdfs:label ?classLabel .
            }
            ORDER BY ASC(?classLabel)""",
            initNs={'rdf': RDF, 'rdfs': RDFS, 'owl': OWL})

    query_individuals = sparql.prepareQuery("""
            SELECT DISTINCT ?individualLabel ?classLabel
            WHERE {
                ?y rdf:type owl:Class .
                ?y rdfs:label ?classLabel .
                ?x rdf:type ?y .
                ?x rdfs:label ?individualLabel .
            }
            ORDER BY ASC(?classLabel)""",
            initNs={'rdf': RDF, 'rdfs': RDFS, 'owl': OWL})

    onto_dict = dict()

    # Process classes
    query_result = g.query(query_classes, DEBUG=True)
    for row in query_result:
        for x in row:
            aspect_class = x.toPython().replace('_', ' ').lower()
            onto_dict[aspect_class] = aspect_class

    # Process individuals
    query_result = g.query(query_individuals, DEBUG=True)
    for row in query_result:
        data_row = []
        for x in row:
            aspect = x.toPython().replace('_', ' ').lower()
            data_row.append(aspect)

        if data_row[0] not in onto_dict:
            onto_dict[data_row[0]] = data_row[1]

    return(onto_dict)


def get_multi_word_aspects(dictionary):
    """
    Return a list of tuples containing only the multi-word aspects in ontology.
    """

    aspect_list = []
    for key in dictionary.keys():
        aspect = key.split(' ')
        if len(aspect) >= 2:
            aspect_list.append(tuple(aspect))

    return(aspect_list)
