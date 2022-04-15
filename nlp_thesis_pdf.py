# -*- coding: utf-8 -*-
"""
NLP Thesis PDF
- Realiza análise NLP em Teses ESALQ
@author: Flotin
"""

###Importa bibliotecas
import pdfplumber, nltk, re, stanza #, NLPyPort
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
#from NLPyPort.FullPipeline import *
from nltk.probability import FreqDist


def filtra_texto(listaPlvrs):
    '''
    Parameters ---------- listaPlvrs : TYPE DESCRIPTION.
    Returns ------- plvsFiltradas : TYPE DESCRIPTION.
    Pega uma lista de palavras e aplica filtros, removendo pontuações, números, SW, etc.
    e devolve a nova lista filtrada
    '''
    plvrMinSemPont = [plv.translate({ord(c): None for c in \
                    pontuacoes}).casefold() for plv in listaPlvrs]
    semPontNumVaz = [p for p in plvrMinSemPont if len(p) > 2 and \
                     p.isdigit() == False]
    plvsFiltradas = [plv for plv in semPontNumVaz if plv not in paraExcluir]
    return plvsFiltradas
    
def extrai_infos():
    #Mostra o número da última página (Contagem da qtd paginas)
    qtdPaginas = pdf.pages[-1].page_number
    #Retorna o ano da publicação
    ano = pdf.pages[0].extract_words()[-1]['text']
    #Extrai o nome do(a) pesquisador(a) OBS: avaliar se outras teses podem ter palavras diferentes de "engenheiro", como variações de genêros e de profissões/cursos
    for word in pdf.pages[1].extract_words():
        if word['text'] != "Engenheiro":
            nomePesquisador += ''.join(word['text']) + ' '
        else: break
    #Registra qual o nível do trabalho (mestrado ou doutorado)
    for word in pdf.pages[1].extract_words():
        if word['text'].lower() == "mestrado" or word['text'].lower() == "doutorado":
            nivelPesquisa += word['text']
            break
    #Extrai o nome do(a) orientador(a)
    #OBS: avaliar se há variação de gênero 'orientadorA' e variação de nível "dissertação"
    primPag = ''.join([val['text'] + ' ' for val in pdf.pages[1].extract_words()]) + ' '
    ini = primPag.index('Orientador:')+12
    nomeOrientador = primPag[ini:ini+primPag[ini:].index('Tese')-1]
    infos = {'Páginas': qtdPaginas, 'Ano': ano, 'Pesquisadora': nomePesquisador, 'Nível': nivelPesquisa, 'Orientador': nomeOrientador}
    return infos
    
def pag_inicial():
    #Encontra a página que o texto da tese inicia, pulando as paginas iniciais
    # Vai ter que ser alterado para acomodar as variações presentes nas teses
    for page in pdf.pages[0:40]:
       for x in range(4):
           try:
               if page.extract_words()[x]['text'].lower() == 'introdução':
                   pgIni = page.page_number - 1
                   return pgIni
           except: None

def tab_freq(listaPlv, dicDestino):
    for plv in listaPlv:
        if plv in dicDestino: dicDestino[plv] += 1
        else: dicDestino[plv] = 1
    #for i in dicDestino: i = i/len(listaPlv) #transforma em porcentagem
    return dicDestino

#inicia variaveis
nivelPesquisa = textoTese = nomePesquisador = nomeOrientador = ''
ini = fim = 0
dicFreqLema = dicFreqRaiz = dicPlvs = dicStanza = {}
lemStanza = []
    
#Abre os PDFs e salva na variável
#import os
#folderpath = r"C:\Users\Flavio\Dropbox\Profissional\Mastera\IA\Teses ESALQ\Teses teste" 
#filepaths  = [os.path.join(folderpath, name) for name in os.listdir(folderpath)]
#for arq in filepaths:
#    pdf = pdfplumber.open(arq)
pdf = pdfplumber.open(r"C:\Users\Flavio\Dropbox\Profissional\Mastera\IA\Teses ESALQ\Teses teste\tese teste.pdf")
#Cria uma string de palavras da tese. #OBS: foi feito só nas primeiras páginas para teste e não sobrecarregar.
for page in pdf.pages[pag_inicial():35]:

    for word in page.extract_words():
        textoTese += ''.join(word['text']) + ' '
# Separa a tese em frases e palavras
frases = sent_tokenize(textoTese)
plvrsTese = word_tokenize(textoTese) 

#Monta a lista do que gostaríamos de excluir/filtrar
pontuacoes = list(punctuation) + ['“', '”', '–']
padraoRefs = r'\(([^"\)]*|\bAnonymous\b|"[^"\)]*")(, )([\d]+|n\.d\.|[\d]+[\w])\)'
results = re.finditer(padraoRefs, textoTese)
refsParenteses = [textoTese[match.start(): match.end()] for match in results]
paraExcluir = stopwords.words('portuguese') + stopwords.words('english') \
    + refsParenteses

#Reduz palavras às suas raízes
raizPlvs = [nltk.stem.RSLPStemmer().stem(plv) for plv in \
            filtra_texto(plvrsTese)]

######Lemma

###biblio Stanza
#stanza.download('pt')
nlp = stanza.Pipeline('pt')
texto = '' #usando só um trecho para testes
for fras in frases[:5]: texto += ''.join(fras) + ' '
for sent in nlp(texto).sentences:
    for word in sent.words:
        dicStanza[word.text] = [word.upos, word.lemma]
        lemStanza.append(word.lemma)

###biblio NLPyPort - precisa rodar em versão mais antiga do NLTK, salva
#no ambeinte NLP ou buscar outra solução, como try except etc,
#configPyPt = {"tokenizer" : True, "pos_tagger" : True, "lemmatizer" : True, "entity_recognition" : True, "np_chunking" : True, "pre_load" : False, "string_or_array" : True}
#text=new_full_pipe(texto, options=options)
#for ind, plv in enumerate(text.tokens):
#   testePyPort[plv] = [text.pos_tags[i], text.lemas[i], ind]

# Cria a tabela de frequência
dicFreqRaiz = tab_freq(raizPlvs, dicFreqRaiz)
dicFreqLema = tab_freq(lemStanza, dicFreqLema)

#Outro metodo de criar tabela de freq
freqRaiz = FreqDist(raizPlvs)
freqLema = FreqDist(lemStanza)

#Encontra duplas de palavras, apartir do score
#bigram_measures = nltk.collocations.BigramAssocMeasures()
#finder = BigramCollocationFinder.from_words(plvsFiltradas)
#sorted(finder.above_score(bigram_measures.raw_freq, 2 / len(tuple(nltk.bigrams(plvsFiltradas)))))
