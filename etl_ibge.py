from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import requests

def extrair():
    # Dicionário que vai conter o resultado de ambas consultas
    geral = {}

    # Consulta da API
    endpoint = 'https://servicodados.ibge.gov.br/api/v1/localidades/estados/MG/municipios'
    response = requests.get(endpoint).json()
    
    # Amarzena em um dicionário contendo nome e id
    municipios_api = [{ 'id': municipio['id'], 'nome': municipio['nome'] } for municipio in response ]

    # Ordena em ordem alfabética
    municipios_api = sorted(municipios_api, key=lambda x: x['nome'])

    # Consulta sparql
    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')

    query = '''
        SELECT ?municipioLabel ?populacao WHERE {
            ?municipio wdt:P31 wd:Q3184121;       # Instância de município do Brasil
                        wdt:P131 wd:Q39109;           # Localizado em Minas Gerais (Q39109)
                        wdt:P1082 ?populacao.       # População

            SERVICE wikibase:label { bd:serviceParam wikibase:language "pt,en". }
        }
    '''

    # Configurações da consulta
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)

    # Consulta
    query = sparql.query().convert()['results']['bindings']

    # Armazena em um dicionário contendo população e nome
    municipios_sparql = [{ 'população': int(municipio['populacao']['value']), 'nome': municipio['municipioLabel']['value'] } for municipio in query ]

    # Ordena em ordem alfabética
    municipios_sparql = sorted(municipios_sparql, key=lambda x: x['nome'])

    # Armazena em array geral
    geral['api'] = municipios_api
    geral['sparql'] = municipios_sparql

    return geral

def transformar(dados):
    # Separa os dados
    api = dados['api']
    sparql = dados['sparql']

    # Array contendo tranformação
    limpo = []

    for i in range(len(api)):
        j = 0
        while(api[i]['nome'] != sparql[j]['nome']):
            if j == len(sparql)-1:
                break
            j += 1
        
        limpo.append({ 'id': api[i]['nome'], 'nome': api[i]['nome'], 'população': sparql[j]['população']})
        sparql.pop(j)

    return limpo

dados = extrair()
dados_limpos = transformar(dados)

# Cria df no pandas
colunas = ['id', 'nome', 'população']
df = pd.DataFrame(dados_limpos, columns=colunas)

# Armazena em csv
df.to_csv('municipios_tratados.csv', index=False)

print('Dados do relatório')
print(f'Quantidade de municípios processados: {len(df)}')
print(f'Média populacional: {df["população"].mean():.2f}')