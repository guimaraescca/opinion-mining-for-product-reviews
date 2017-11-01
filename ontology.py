"""
Class and functions to query data from OWL Ontologies.
"""

# Third party libraries
import rdflib
from rdflib.namespace import RDF, OWL


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
