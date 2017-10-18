import rdflib
from rdflib.namespace import RDF, RDFS

namedIndividual = rdflib.URIRef('http://www.w3.org/2002/07/owl#NamedIndividual')
owl_class = rdflib.URIRef('http://www.w3.org/2002/07/owl#Class')
_class = rdflib.URIRef("http://webprotege.stanford.edu/R8O4nH6gJk5iCmlDBigLLVw")
_type = rdflib.URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
_literal = rdflib.term.Literal('leve')

# Load ontology
ontology_path = 'ontologies/smartphone_aspects.owl'
g = rdflib.Graph()
g.load(ontology_path)

# Buscar todas as instancias de uma categoria
subjects = g.transitive_subjects(_type, _class)
for item in subjects:
    print(g.label(item))

# Listar todos os sujeitos
subjects = g.subjects(_type)
for item in subjects:
    print(g.label(item))

# Example of comparison between labels of different types
literal = rdflib.term.Literal('leve')
literal_uri = rdflib.URIRef('leve')
# print(g.label(_literal)==g.label(literal_uri))

# Search for every relation 'belongs to class' between aspects and classes
for b in g.subject_objects(_type):
    # Select results that are not individuals or classes
    if b[1] != namedIndividual and b[1] != owl_class:
        # Select relation with that contains the searched aspect
        if g.label(b[0]) == _literal:
            print(f'Search aspect:{g.label(b[0])} \tCategory:{g.label(b[1])}')

# Another method to search for an aspect category
for triple in g.triples((None, None, _literal)):
    print(f'{triple}\n')
    for triple2 in g.triples((triple[0], _type, None)):
        if triple2[2] != namedIndividual:
            print(f'[{g.label(triple2[2])}]')
