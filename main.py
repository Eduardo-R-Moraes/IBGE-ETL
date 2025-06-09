from SPARQLWrapper import SPARQLWrapper, JSON
import requests

def get_api():
    endpoint = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios'
    municipios = requests.get(endpoint).json()
    
    resp = {municipio['id']: municipio['nome'] for municipio in municipios}

    return resp

def sparql():
    sparql = SPARQLWrapper('https://query.wikidata.org/')

    query = '''
        SELECT ?municipioLabel ?populacao WHERE {
            ?municipio wdt:P31 wd:Q3184121;       # Instância de município do Brasil
                        wdt:P131 wd:Q175;           # Localizado em São Paulo (Q175)
                        wdt:P1082 ?populacao.       # População

            SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
        }
        ORDER BY DESC(?populacao)
    '''

    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)

    return sparql.query()

print(sparql())