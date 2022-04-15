# -*- coding: utf-8 -*-
"""
Webscrap 
- Realiza o webscrapping das informações das tese
- Realiza o download dos pdfs das teses

@author: Flotin Yara - float@flotin.br
"""

#####Webscrapping
#####Criando a base de dados de Teses USP, a partir do site https://www.teses.usp.br/index.php?option=com_jumi&fileid=30&Itemid=162&lang=pt-br&id=11

#importa bibliotecas
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from time import sleep
from numpy import random
import os

def abre_pag(url):
    '''
    Parameters
    ----------
    url : TYPE DESCRIPTION.
    
    Returns
    -------
    soup : TYPE DESCRIPTION.
    '''
    sleep(3.0 +  random.uniform(0,2))
    link = Request(url,headers={'User-Agent': 'Mozilla/5.0'})
    pagina = urlopen(link).read().decode('utf-8', 'ignore')
    soup = BeautifulSoup(pagina, "lxml")
    return soup

def lista_html_ahref(classe, link, ini=0):
    listing = abre_pag(link).find_all("div", attrs={"class": classe})
    listing = [i for i in listing[ini:]]
    listaRetorno = []
    for li in listing:
        if li.a:
            listaRetorno.append(li.a['href'])
    return listaRetorno

def obtem_infos_tabela_tese(info,stop=None):
    for index, item in enumerate(listing5):
        if info in item.text.lower():
            return listing6[index].text[:stop]

#Cria a primeira lista dos links com as paginas da lista de resultado
#de departamentos
linksPagsDeptos = ['https://www.teses.usp.br/index.php?option=com_jumi&fileid=30&Itemid=162&lang=pt-br&id=11&pagina=' \
                   + str(x) for x in range(6)[1:]]

#Inicia variáveis
linksCadaDepartamento = []
linksPagsTodosDeptos = []
linksTeses = []
linksPDF = []
dadosTeses = {}

#Salva os conteudos html
for indice, linkPag in enumerate(linksPagsDeptos):
    print('fase 1 - '+str(indice+1)+' de '+ str(len(linksPagsDeptos)))
    #Extrai o conteúdo de link das páginas de cada unidade
    linksCadaDepartamento += ['https://www.teses.usp.br' + x for x \
                    in lista_html_ahref('dadosAreaNome', linkPag, 1)]
    
#Abre cada departamento para criar lista de links das paginas do depto
#slicing utilizado para reduzir o tamanho, somente para utilizar na fase de testes
for indice, linkDep in enumerate(linksCadaDepartamento[9:12]): 
    print('fase 2 - '+str(indice+1)+' de '+str(len(linksCadaDepartamento[9:12])))    
    #Define a quantidade de páginas da lista de resultados de tese do Dep.    
    listing2 = abre_pag(linkDep).find_all("div", attrs={"class": "dadosLinha"})
    stri = str(listing2[-1])
    qtdPagsDep = range(int(stri[stri.index('de',56)+3:-6])+1)[1:]    
    #Cria uma lista com os links da página de resultado dos departamentos
    linksPagsTodosDeptos += [linkDep + '&pagina=' + str(pagi) for pagi \
                               in qtdPagsDep]

#Abre todas as páginas de todos deptos da ESALQ
for indice, url in enumerate(linksPagsTodosDeptos):
    print('fase 3 - '+str(indice+1)+' de '+str(len(linksPagsTodosDeptos)))    
    #Pega o link da pagina virtual de cada tese individual
    linksTeses += lista_html_ahref('dadosDocNome', url)
                      
#Abre o link de todas as teses
for indice, url2 in enumerate(linksTeses):
    print('fase 4 - '+str(indice+1)+' de '+str(len(linksTeses)))    
    #Obtém link do PDF da tese
    linkPDF = 'https://www.teses.usp.br' + \
        str(lista_html_ahref('DocumentoTituloTexto2', url2)[0])
    linksPDF += [linkPDF]
            
####Obtém infos da tese
    listing5 = abre_pag(url2).find_all("div", attrs={"class": "DocumentoTituloTexto"}) 
    listing6 = abre_pag(url2).find_all("div", attrs={"class": "DocumentoTexto"}) 
    nomePesquisadora = obtem_infos_tabela_tese('nome completo')
    nivel = obtem_infos_tabela_tese('documento')
    tituloTese = obtem_infos_tabela_tese('título em português')
    palavrasChave = obtem_infos_tabela_tese('palavras-chave')
    areaConheci = obtem_infos_tabela_tese('conhecimento')
    ano = obtem_infos_tabela_tese('data',stop=4)
    orientadores = obtem_infos_tabela_tese('orientador')
    doi = obtem_infos_tabela_tese('doi')
    #Faz o download das teses
    response = requests.get(linkPDF)
    pdf = open(str(nomePesquisadora)+str(ano)+".pdf", 'wb')
    pdf.write(response.content)   
    pdf.close()              
#Salva as infos em um dicionário
    dadosTeses[tituloTese] = nomePesquisadora, areaConheci, \
    ano, nivel, doi, linkPDF
    
    
#Realiza download das teses#######################
#os.chdir(r'C:\Users\Flavio\Desktop\Trabai\Big data\NLP teses download PDF teste')
#for link in linksPDF:
#   response = requests.get(link)
#   pdf = open(str(tituloTese)+".pdf", 'wb')
#   pdf.write(response.content)   
#   pdf.close()
#
