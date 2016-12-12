# -*- coding: cp1252 -*-
#Versao: 2016-05-06
#        AAAA-MM-DD
"""
Nome:        Hydrolib.py versao 1.0

Objetivo:    Biblioteca didatica para a estimativa de funcoes hidrologicas, 
             disponivel na Internet como codigo aberto, permitindo um ambiente 
             colaborativo para o desenvolvimento de modelos hidrologicos 
             e sua interacao com ferramentas SIG. 

Authores:    Daniel Allasia <dga@ufsm.br>, Vitor Geller <vitorgg_hz@hotmail.com>
             Rutineia Tassi, Lucas Tassinari
             
Copyright:   (c) Daniel Allasia, Vitor Geller, Rutineia Tassi, Lucas Tassinari

================================================================================
Licenca:

    Este programa/biblioteca e um software livre; voce pode redistribui-lo e/ou 
    modifica-lo dentro dos termos da Licenca Publica Geral GNU como 
    publicada pela Fundacao do Software Livre (FSF); na versao 2 da 
    Licenca, ou (na sua opiniao) qualquer versao.

    Este programa e' distribuido na esperanca de que possa ser util, 
    mas SEM NENHUMA GARANTIA; sem uma garantia implicita de ADEQUACAO a qualquer
    MERCADO ou APLICACAO EM PARTICULAR. Veja a 
    Licenca Publica Geral GNU para maiores detalhes.

    Voce deve ter recebido uma copia da Licenca Publica Geral GNU
    junto com este programa, se nao, escreva para a Fundacao do Software
    Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.

================================================================================
Description:


  Os metodos aqui descritos estao basados em diferentes fontes de informacao 
  que sao citados dentro de cada biblioteca

================================================================================
Quadro resumo das funcoes da biblioteca:
    
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                NOME                |                                            DESCRICAO                                                  |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
| calcular_PrecipitacaoDesacumulada  |    Calcula a Intensidade a partir da relacao Intensidade-duracao-frequencia (IDF).                    |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|      aplicar_BlocosAlternados      |    Redistribui a chuva de projeto conforme a metodologia dos blocos alternados.                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |    Aplica o metodo de separacao do escoamento superficial pelo metodo desenvolvido pelo National      |
|  calcular_PrecipitacaoEfetiva_CN   |Resources Conservation Center dos EUA (antigo Soil Conservation Service - SCS), apresentado por        |
|                                    |Collischonn e Tassi, 2013.                                                                             |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|         calcular_TC_Kirpich        |    Estima o tempo de concentracao para pequenas bacias pela equacao de Kirpich (menores que 0.5 km^2).|
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|          calcular_HUT_SCS          |    Calcula parametros do hidrograma unitario triangular sintetico.                                    |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|         aplicar_Convolucao         |    Calcula o hidrograma de projeto a partir de de uma serie de dados de chuva efetiva.                |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |    Funcao responsavel por plotar e salvar os graficos gerados nas operacoes chuva-vazao.              |
|        plotar_Hidrogramas_PQ       |    Sao plotados dois graficos para cada bacia cujo os dados foram gerados a partir de uma equacao     |
|                                    |intensidade-duracao-frequencia (IDF).                                                                  |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |    Funcao responsavel por plotar e salvar o grafico gerado na modelagem dos cenarios.                 |
|         plotar_Cenarios_PQ         |    E' plotado um grafico (com uma curva para cada ano simulado) para cada bacia.                      |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|      calcular_VazaoSaida_Puls      |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|            aplicar_Puls            |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|       plotar_Hidrogramas_PULS      |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|     aplicar_MuskingunCunge         |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|     plotar_Hidrogramas_MKC         |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|         somar_Hidrogramas          |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|     plotar_somar_Hidrogramas       |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|      aplicar_MetodoSilveira        |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|
|                                    |                                                                                                       |
|      aplicar_PenmanMonteith        |                                                                                                       |
|                                    |                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------------------|

"""
 
#Precipitacao desacumulada 
  
def calcular_PrecipitacaoDesacumulada(nint_tempo_chuva, dt,TR,a,b,c,d):
    """
    Calcula a chuva desacumulada a partir da IDF a seguir:
 
        I [mm/h] = ( a.TR^b ) / ( (t+c)^d )
        
    A funcao retorna a precipitacao desacumulada em uma variavel do tipo lista
        Pdes = [...]

    Parametros para uso:
        
            nint_tempo_chuva: Variavel do tipo inteiro que armazena o numero de intervalos de tempo COM CHUVA da operacao.
            
            dt: Variavel do tipo inteiro que armazena a duracao do intervalo de tempo [em segundos].
            
            TR : Variavel do tipo inteiro que armazena o tempo de retorno [anos].
            
            a,b,c,e: Variaveis do tipo float que armazenam os valores dos parametros da IDF.
    """
    
    #Algoritmo original escrito por Lucas Tassinari, revisado e otimizado por Vitor Geller.
    
    #evito divisao inteira
    dt=float(dt)
    TR=float(TR)
    
    Pdes = [0.0 for i in xrange(nint_tempo_chuva)]

    Pacum = [a*TR**b/((i*dt/60.+c)**d)*i*dt/3600.0 for i in xrange(1, (nint_tempo_chuva+1))]   #calcula a Precipitacao a partir da IDF- transformado dt em segundos
    
    Pdes[0] = Pacum[0]
    for i in xrange(1, nint_tempo_chuva):
        Pdes[i] = Pacum[i] - Pacum[i-1]  #Precipitacao desacumulada
    
    return Pdes
#_______________________________________________________________________# 
#

def aplicar_BlocosAlternados(Pdes, nint_tempo_chuva, pospico):
    """
    Aplica o metodo dos blocos alternados a partir de uma serie de dados de chuva desacumulada e retorna a precipitacao ordenada.
    
    No metodo dos blocos alternados, os valores incrementais sao reorganizados 
    de forma que o maximo incremento ocorra, aproximadamente, no meio da duracao 
    da chuva total. Os incrementos (ou blocos de chuva) seguintes sao organizados 
    a direita e a esquerda alternadamente, ate preencher toda a duracao, segundo 
    Collischonn e Tassi, 2013.
    
    Esta funcao retorna a chuva ordenada em uma variavel do tipo lista
        Pord = [...]

    Parametros para uso:
        
            Pdes: Lista que contem os dados de chuva desacumulada.
                -> Esta variavel deve ser estruturada da seguinte forma:
                Pdes = [...] -> Dados de chuva desacumulada [em mm/s].
                OBS: A variável Pdes DEVE estar em ordem DECRESCENTE.
            
            nint_tempo_chuva: Variavel do tipo inteiro que armazena o numero de intervalos de tempo COM CHUVA da operacao.
            
            pospico: Variavel do tipo float que armazena a posicao da maior precipitacao desacumulada em porcentagem decimal.
                 
                 Exemplo: pospico = 0.5 -> Pico em 50 porcento do tempo da simulacao
                          pospico = 0.2 -> Pico em 20 porcento do tempo da simulacao
    """

    #Algoritmo original escrito por Daniel Allasia, revisado e otimizado por Vitor Geller.
    
#    import tkMessageBox
    from tkMessageBox import showinfo
    import sys
    
    
    # Ordena a chuva pelo metodo dos blocos alternados
    
    #   Se o pospico nao esta no range correto
    if (float(pospico) < 0 or float(pospico) > 1):
        showinfo("Erro", "O valor do pico de chuvas (pospico) deve estar entre zero e um (0 <= pospico <= 1).\n\nO modelo será finalizado, tente novamente.") #"Voce e' burro." ahahhahahaha
        sys.exit()
    
    #   Se o tamanho de Pdes nao e' igual ao numero de intervalos de tempo com chuva
    if len(Pdes) != nint_tempo_chuva:
        showinfo("Erro", "O numero de intervalos de tempo com chuva deve ser igual ao tamanho da série de precipitações desacumuladas.\n\nO modelo será finalizado, tente novamente.") #"Voce e' burro." ahahhahahaha
        sys.exit()

    #   Se nao parou ate' aqui, continue...
    
    #   Se pospico for zero
    if (float(pospico) == 0.0):
        indice_pico = 0

    #   Se nint_tempo_chuva for par
    elif nint_tempo_chuva % 2 == 0:
        indice_pico = (int(pospico*nint_tempo_chuva)-1)   #estimo a localizacao do pico em numero de intervalos de tempo com relacao a duracao da chuva
        
    #   Se nint_tempo_chuva for impar
    elif nint_tempo_chuva % 2 == 1:
        indice_pico = int(pospico*nint_tempo_chuva)   #estimo a localizacao do pico em numero de intervalos de tempo com relacao a duracao da chuva
        
    Pord             = [0. for x in xrange(len(Pdes))] # armazenar os valores. Variavel retornada no final da funcao.
    indice_pdes      = 0 #variavel de posicao
    indice_ordenacao = 1 #variavel de posicao
    
    Pord[indice_pico] = Pdes[indice_pdes] #(Valor central se impar.... se par: arredondado para baixo) correspondente ao primeiro valor da chuva desacumulada (maior valor)
    
    #   Fazer o loop N vezes ate' que o bloco caia "fora" nos dois extremos
    while ( ((indice_pico - indice_ordenacao) >= 0) or ((indice_pico + indice_ordenacao) <= (len(Pdes))) ):
        
        #   Comeco loop sempre verificando se e' possivel colocar um valor na direita do pico
        if (indice_pico + indice_ordenacao) < len(Pord): # se for == ele nao entra
            indice_pdes += 1  # aumentar o indice de pdes em uma unidade para poder copiar o proximo valor de pdes
            Pord[(indice_pico + indice_ordenacao)] = Pdes[indice_pdes] # Entro com o valor na direita se for possivel
            
        #   Verifico se e' possivel colocar um valor a esquerda do pico
        if (indice_pico - indice_ordenacao) >= 0: # aqui pode ser igual, porque trata-se de indice (o primeiro e' zero)
            indice_pdes += 1 # Aumentar o indice de pdes em uma unidade para poder copiar o proximo valor de pdes
            Pord[(indice_pico - indice_ordenacao)] = Pdes[indice_pdes]   #valor abaixo se o indice nao for menor que zero

        indice_ordenacao += 1 # preparar para o proximo loop
    
    return Pord
#_______________________________________________________________________#     
#Precipitacao de Projeto Acumulada

def calcular_PrecipitacaoEfetiva_CN(CN, Pord, nint_tempo, nint_tempo_chuva):
    """
    Aplica o metodo de separacao do escoamento superficial pelo metodo desenvolvido 
    pelo National Resources Conservation Center dos EUA (antigo Soil Conservation Service - SCS)
    segundo Collischonn e Tassi, 2013.
    
    A funcao retorna a precipitacao efetiva em uma variavel do tipo lista
        Pef = [...]
        
    Parametros para uso:
        
            CN: Variavel do tipo float que armazena o parametro adimensional tabelado que varia de 0 a 100.
            
            Pord: Lista que contem os dados de chuva ordenada.
                -> Esta variavel deve ser estruturada da seguinte forma:
                Pord = [...] -> Dados de chuva ordenada [em mm/s].
            
            nint_tempo: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            
            nint_tempo_chuva: Variavel do tipo inteiro que armazena o numero de intervalos de tempo COM CHUVA da operacao. (nint_tempo_chuva<=nint_tempo).
            
    """
    
    #Algoritmo original escrito por Lucas Tassinari, revisado e otimizado por Vitor Geller.
        
    S = 25400.0/CN - 254 #mm
    Ia = 0.2*S #mm. Armazenamento maximo do solo
    
    Pord_acum = [0.0 for i in xrange (nint_tempo_chuva)] #declarar variavel
    
        #acumulo a chuva para verificar se o que choveu e' maior que Ia
    Pord_acum[0] = Pord[0]
    for i in xrange (1, nint_tempo_chuva):
        Pord_acum[i] = Pord_acum[(i-1)] + Pord[i]  #e' o que ja' esta' acumulado + o que eu devo acumular neste intervalo de tempo.
           
        #Caso adicionado por Lucas Tassinari, corrigida por Vitor Geller. 
        #Caso numero de intervalos de tempo com chuva for menor que os intervalos de tempo.
    if (nint_tempo_chuva < nint_tempo):                  # completa com chuva nula
        for i in xrange (nint_tempo_chuva, nint_tempo): # linha corrigida
            Pord_acum.append(0) #linha corrigida
            
        #Precipitacao efetiva acumulada SCS - Modificado por Vitor Geller.
    Pef_acum =[0.0 for i in xrange (nint_tempo)]             #cria a matriz
    for i in xrange (nint_tempo):
        if Pord_acum[i] > Ia:
            Pef_acum[i] = ((Pord_acum[i] - Ia) ** 2)/float((Pord_acum[i] - Ia + S))
        else:
            Pef_acum[i] = 0.0  #somente gera escoamento se a lamina acumulada for maior que Ia, faz parte do metodo... Antes de Ia toda a precipitacao infiltra.
           
        #Desacumulo a chuva efetiva
    Pef = [0.0 for i in xrange (nint_tempo)]    # Bug: Quando nint_tempo > nint_tempo_chuva esta linha nao funciona - Vitor G. Geller
#    Pef = [0.0 for i in xrange (nint_tempo_chuva)] # Correcao do bug descrito acima - Vitor G. Geller
    Pef[0] = Pef_acum[0]
    for i in xrange (1, nint_tempo_chuva):
        Pef[i] = Pef_acum[i] - Pef_acum[(i-1)]
        
    return Pef      

############################################# - INICIO ALGORITMO ORIGINAL
### por Lucas Tassinari. (adicione/remova "##" de cada linha para desativar/ativar)    
##  
##    S = 25400.0/CN - 254 #mm
##    Ia = 0.2*S #mm. Armazenamento maximo do solo
##    #acumulo a chuva
##    Pacum = [0.0 for i in xrange (nint_tempo)]             
##    Pacum [0] = Pord[0]
##    for i in xrange (1,nint_tempo_chuva):
##        Pacum [i] = Pacum[i-1]+Pord[i]

##    if (nint_tempo_chuva<nint_tempo):     # Adicionado por Vitor G. Geller... completa com chuva nula
##        for i in xrange (nint_tempo_chuva,nint_tempo-1):
##            Pacum [i] = Pacum[nint_tempo_chuva-1]
##    
##    #Precipitacao efetiva acumulada SCS    
##    Pef_acum =[0.0 for i in xrange (nint_tempo-1)]             #cria a matriz
##    for i in xrange (0,nint_tempo-1):
##        if Pacum[i]>= Ia:
##            Pef_acum[i] = (Pacum[i]-Ia)**2/(Pacum [i]-Ia+S)
##        else:
##            Pef_acum[i] = 0.0     
##           
##    #desacumulo a chuva efetiva
##    Pef = [0.0 for i in xrange (nint_tempo-1)]             
##    Pef [0] = Pef_acum[0]
##    for i in xrange (1,nint_tempo-1):
##        Pef [i] = Pef_acum[i]-Pef_acum[i-1]        
##          
###    return Pef, Pacum, Pef_acum #removito por Vitor G. Geller
##    return Pef
##
############################################# - FIM ALGORITMO ORIGINAL
#_______________________________________________________________________#         
#Tempo de Concentracao Kirpich

def calcular_TC_Kirpich(DIFERENCA_COTA, COMPRIMENTO_CANAL):
    """
    Equacao de Kirpich desenvolvida empiricamente para estimar o tempo de concentracao de pequenas bacias (menores que 0.5 km^2).
    
    A funcao retorna o resultado estimado para o tempo de concentracao em HORAS em uma variavel do tipo float!
    
    Parametros para uso:
        
            DIFERENCA_COTA: Variavel do tipo float que armazena a diferenca de altitude ao longo do curso d'agua principal [metros].
        
            COMPRIMENTO_CANAL: Variavel do tipo float que armazena o comprimento do curso d'agua principal [quilometros].
    """
    
    #Algoritmo original escrito por Lucas Tassinari.
    
    tc = (57*((COMPRIMENTO_CANAL**3)/DIFERENCA_COTA)**0.385)/60.0   #Tempo de concentracao em HORAS
    
    return tc
#_______________________________________________________________________#     
#Caracteristicas do HUT para propagacao do escoamento

def calcular_HUT_SCS(TC,AREA,dt):
    """
    Retorna valores (Tempo de subida [horas], Vazao de pico [horas] e Tempo de base [horas]) do hidrograma unitario sintetico.
    
    Todas as variaveis retornadas por esta funcao sao do tipo float.
    
    Parametros:
        
            TC: Variavel do tipo float que armazena o tempo de concentracao da bacia [horas].
            
            AREA: Variavel do tipo float que armazena a area da bacia [km^2].
            
            dt: Variavel do tipo inteiro que armazena a duracao do intervalo de tempo [em segundos].
    """
    
    #Algoritmo original escrito por Lucas Tassinari, revisado e otimizado por Vitor Geller.
    
    Tempo_pico = 0.6*TC #TC em HORAS!
    Tempo_subida = Tempo_pico + dt/7200.0 #O digo "Tp" da maioria dos livros. Tempo total de subida, desde origem.
    Vazao_pico_HUT = 0.208*AREA/Tempo_subida  #Vazao de pico em 
    Tempo_base = 2.67*Tempo_subida

    return Tempo_subida, Vazao_pico_HUT, Tempo_base
#_______________________________________________________________________#
def aplicar_Convolucao(Tempo_base, Vazao_pico_HUT, Tempo_subida, dt, nint_tempo, Pef):
    """
    Calcula o hidrograma de projeto a partir de uma serie de dados de chuva efetiva.
    
    O hidrograma e' retornado em uma variavel do tipo lista [em m³/s].
        hidrograma = [...]
    
    OBS: E' necessario informar dados basicos do hidrograma unitario sintetico para efetuar a convolucao.
    
    Parametros para uso:
        
            Tempo_base: Variavel do tipo float que armazena o tempo total do HUT (toda a base do triangulo, da origem ao fim) [horas].
            
            Vazao_pico_HUT: Variavel do tipo float que armazana a vazao de pico do HUT (maior ordenada do triangulo) [m3/s].
            
            Tempo_subida: Variavel do tipo float que armazana o tempo total de subida do HUT, desde sua origem [horas].
            
            dt: Variavel do tipo inteiro que armazena a duracao do intervalo de tempo [em segundos].
            
            nint_tempo: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            
            Pef: Lista que contem os dados de chuva efetiva.
                -> Esta variavel deve ser estruturada da seguinte forma:
                Pef = [...] -> Dados de chuva efetiva [em mm/s].
    """
    
    #Algoritmo original escrito por Lucas Tassinari, revisado e otimizado por Vitor Geller.

############################################# - INICIO ALGORITMO ORIGINAL
### por Lucas Tassinari. (adicione/remova "##" de cada linha para desativar/ativar)
###   
##    
##    tempo_hora = [(dt*i/3600.0) for i in xrange(nint_tempo)]    
##    HU = [0. for i in xrange(nint_tempo)]  
##    a_s = (float(Vazao_pico_HUT)/Tempo_subida)
##    a_d = float (- Vazao_pico_HUT/ (Tempo_base * (1- (Tempo_subida/Tempo_base))))
##    b_d = float (Vazao_pico_HUT/(1 - (Tempo_subida/Tempo_base)))      
##    
##    
##    for i in xrange(nint_tempo):
##        if (tempo_hora[i]<=(Tempo_subida)):                             #Estabelece hidrograma para a curva de subida
##            HU[i] = a_s*tempo_hora[i]
##                
##        elif ((tempo_hora[i]>Tempo_subida) and (tempo_hora[i]<=Tempo_base)):   # Estabelece hidrograma para a curva de descida ate tempo = Tempo de Base do HUT
##            HU[i] = a_d * tempo_hora[i] + b_d
##                    
##
##    convolucao = []
##    for colunas in xrange(nint_tempo):  #for colunas in xrange(nint_tempo):
##        P_aux = [0.0 for i in xrange(nint_tempo)] 
##        for i in xrange(nint_tempo-1-colunas):
##            P_aux[(i+colunas)] = Pef[colunas]*HU[i]
##        convolucao = (convolucao + [P_aux]) #Linha modificada por Vitor G. Geller, ela adiciona P_aux como sendo um nova coluna na lista da convolucao
##        
##            #Fazer o somatorio das linhas da convolucao
##    n1 = 0
##    hidrograma = array([float(0) for i in xrange(0, nint_tempo,1 )], float64)   
##    for linha in xrange(0, len(convolucao[0])):  #linha e fixo, varia a coluna, !!!!ATENcaO: CONSIDERANDO TODAS AS COLUNAS COM O MESMO NÚMERO DE LINHAS!!!!!!
##       for coluna in xrange(0, len(convolucao)):
##            valor = convolucao[coluna][linha]  #pega valor de cada linha
##            n1 = valor + n1  #soma eles
##        hidrograma[linha] = float(n1)
###        hidrograma.append(n1) #adiciona-se na lista - LINHA DESATIVADA
##        n1 = 0 #reseta-se a soma  
##
############################################# - FIM ALGORITMO ORIGINAL
############################################# - INICIO ALGORITMO OTIMIZADO
### escrito por Vitor G. Geller (adicione/remova "##" de cada linha para desativar/ativar)

    from numpy import array, float64
    
    #   Variavel para armazenar os valores do HU Sintetico
    HU = [0. for i in xrange(nint_tempo)] 
    
    #   Coeficientes das retas que formam o HU Sintetico
    coef_A_subida = float(Vazao_pico_HUT)/Tempo_subida
#    coef_B_subida = 0. #Nao tem - esta' aqui para lembrar o programador de que o HU e' um triangulo e pode ser representado por duas retas
    coef_A_descida = - float(Vazao_pico_HUT)/(1.67*Tempo_subida)
    coef_B_descida = 2.67*Vazao_pico_HUT/1.67 # coef_B_descida = float(Tempo_base * Vazao_pico_HUT) / Tempo_subida
    
    for i in xrange(nint_tempo):
        tempo_em_horas = (dt*i/3600.0)
        
        #   Avaliar qual das retas utilizar.
        if (tempo_em_horas <= (Tempo_subida)): #ambos em HORAS
            HU[i] = coef_A_subida * tempo_em_horas #caiu na reta de subida
        
        #   Curva descendente - > 
        else:
            HU[i] = ((coef_A_descida * tempo_em_horas) + coef_B_descida) #caiu na reta de descida
            
            #   Se o valor calculado do HUT for negativo (pode acontecer em funcao da aproximacao decimal) troque seu valor para zero
            if HU[i] < 0.0:  # Este caso acontece quando nint_tempo > nint_tempo_chuva ;)
                HU[i] = 0.0  # A reta de descida e' calculada ate' tocar o eixo X. Se a reta atrassar para o 4 quadrante, seu valor deve ser corrigido
    
        #NOVO ALGORITMO DE CALCULO DA CONVOLUCAO (algoritmo otimizado para calculo do hidrograma de projeto), Este algoritmo trabalha com a convolucao em linhas. 
    
    cont_conv = 1 #VARIAVEL QUE CONTA QUANTAS COLUNAS SERAO CALCULADAS NESTA LINHA DA CONVOLUCAO...COMECA EM 1 POIS PYTHON COMECA A CONTAR EM ZERO!!
    hidrograma = array([0.0 for i in xrange(nint_tempo)], float64) #variavel que armazena os valores do hidrograma de projeto
    convolucao = [0.0 for i in xrange(nint_tempo)] #a convolucao agora e' calculada de linha em linha.
    
    for linha in xrange(nint_tempo):
        for coluna in xrange(cont_conv):
            
            #           CONVOLUCAO
            #           Q1 = Pef1.h1                                         = (Valor do hidrograma em dt = 1)
            #           Q2 = Pef2.h1 + Pef1.h2                               = (Valor do hidrograma em dt = 2)
            #           Q3 = Pef3.h1 + Pef2.h2 + Pef1.h3                     = (Valor do hidrograma em dt = 3)
            #           Q4 =           Pef3.h2 + Pef2.h3 + Pef1.h4           = (Valor do hidrograma em dt = 4)
            #           Q5 =                     Pef3.h3 + Pef2.h4 + Pef1.h5 = (Valor do hidrograma em dt = 5)
            #           (Introduzindo Hidrologia, IPH UFRGS, Agosto 2008, p.115, Walter Collischonn, Rutinéia Tassi)
            
            #A proxima linha calcula a a linha da convolucao de trás para frente; Exemplo: Para Q3: calcula-se Pef1.h3, em seguida Pef2.h2 e por final Pef3.h1.
            convolucao[coluna] = Pef[coluna]*HU[(linha-coluna)] #para calcular o hidrograma de projeto (linha da convolucao), multiplica-se cada valor de chuva efetiva pelo valor de HU correspondente.
            
        cont_conv += 1 #PROXIMA LINHA CALCULAREI UMA COLUNA A MAIS, SENDO ATE' UM MAXIMO DE nint_tempo (PRESENTE NO LOOP ANTERIOR)
        hidrograma[linha] = sum(convolucao) #o valor do hidrograma de projeto no intervalo de tempo T, e' a soma da linha da convolucao neste mesmo intervalo de tempo (assumido por "linha").
##
############################################# - FIM ALGORITMO OTIMIZADO

    #   Retorna o hidrograma calculado (arranjo e' um vetor com nint_tempo valores)
    return hidrograma
    
#_______________________________________________________________________#

def plotar_Hidrogramas_PQ(Hidrograma, Pord, Pef, nint_tempo, dt, caminho_saida, nome_posto, numero_do_grafico):
    """
    Funcao responsavel por plotar e salvar os hidrogramas calculados nas operacoes chuva-vazao. 
    
    A funcao plota dois graficos toda vez que e' executada:
        O primeiro grafico contem o hietograma de projeto utilizado e o respectivo hidrograma calculado.
        O segundo grafico contem a chuva efetiva juntamente com a informacao da primeira plotagem.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        
            Hidrograma: Lista que contem os dados dos hidrogramas a serem plotados.
                -> Esta variavel deve ser estruturada da seguinte forma:
                Hidrograma = [...] -> Valores de vazao de um hidrograma [em metros^3/s].
                
            Pord: Lista que contem os dados de chuva ordenada.
                -> Esta variavel deve ser estruturada da seguinte forma:
                Pord = [...] -> Dados de chuva ordenada [em mm/s].
                
            Pef: Lista que contem os dados de chuva efetiva.
                -> Esta variavel deve ser estruturada da seguinte forma:
                Pef = [...] -> Dados de chuva efetiva [em mm/s].
            
            nint_tempo: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            
            dt: Variavel do tipo inteiro que armazena a duracao do intervalo de tempo [em segundos].
            
            caminho_saida: Variavel do tipo string que armazena o diretorio em que a imagem sera' salva.
            
            nome_posto: Variavel do tipo string que armazena o titulo do grafico.
            
            numero_do_grafico: Variavel do tipo inteira que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
                -> OBS: Esta variavel deve assumir um valor diferente para cada plotagem. 
                        E' recomendado utilizar o numero da operacao como valor para numero_do_grafico.
                        O nome final do arquivo e': (caminho_saida)/PlotagensPQ/Operacao_(numero_do_grafico)_Puls.png
            
    """
    
    #Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    import os
    from numpy import array, linspace    
    
        
        #Agora que eu deletei a pasta antiga, faca uma nova para salvar os graficos 
    if not os.path.exists(caminho_saida + "/PlotagensPQ"):
        os.makedirs(caminho_saida + "/PlotagensPQ")
        
#    posicao_maximo = 0
#    while Hidrograma[posicao_maximo] != max(Hidrograma):
#        posicao_maximo = posicao_maximo + 1
              
    altura_maxima_grafico = (2 * (max(Hidrograma))) #ajustar a "escala" vertical do grafico
        
    x = array([i for i in xrange( nint_tempo )])  #transforma eixo x em array (primeira plotagem)
                    
    fig = plt.figure(figsize=(15,9), dpi=60)    #inicio da primeira plotagem
    ax1 = fig.add_axes([0.126, 0.1, 0.772, 0.8]) #ajustar a tela
    
    plt.axis([0, nint_tempo, 0, (altura_maxima_grafico)])  #declarar eixos
    ax1.plot(x, Hidrograma, 'b-', linewidth=4, label = 'Vazao de entrada')  #plotagem
        
    ax1.set_xlabel('Intervalos de tempo', size = 15)   #nome do eixo x
    ax1.set_ylabel('Vazao (m3/s)', color='b', size = 15)       #nome e cor do nome do eixo y         
    for corlabel1 in ax1.get_yticklabels():         #trocar a cor dos valores do eixo y
        corlabel1.set_color('b')
            
    grid_horizontal_1 = linspace((0),(altura_maxima_grafico),(5)) #grid horizontal (eixo y)
    grid_vertical = linspace((0),(nint_tempo),(5)) #grid vertical (eixo y)
    
    ax1.xaxis.set_ticks(grid_vertical) #nomear grid
    ax1.yaxis.set_ticks(grid_horizontal_1) #nomear grid
    ax1.grid(True) #Ligar/Desligar o grid
            
        #Serie de valores (0,1,2,3,4,5....) usados como eixos
    segundo_eixo_x = [ i for i in xrange(len(Pord))]  #segundo eixo x (precipitacao ordenada). Foi preciso para criar um eixo para cada hietograma, pois ha casos em que seus tamanhos sao diferentes.
        
        #Serie de valores (0,1,2,3,4,5....) usados como eixos
    terceiro_eixo_x = [ i for i in xrange(len(Pef))] #terceiro eixo x (precipitacao efetiva). Foi preciso para criar um eixo para cada hietograma, pois ha casos em que seus tamanhos sao diferentes.
        
#__________________________________________________________________________________________________________
        #Inverter eixos
    ax2 = ax1.twinx()   
    #--------------------------- 
        #Determinar eixos
    plt.ylim( (max(Pord)*3),0)  #fica como deve ser, mas em tamanho de todo grafico
    
    grid2 = linspace((0),(max(Pord)*3),(5)) #pegar valores para segundo eixo Y     
    plt.yticks(grid2) #Determinar quais valores aparecerao no segundo eixo Y
    #---------------------------    
        #Plotagem
    plt.bar(segundo_eixo_x, Pord, width = 1, color='r', linewidth = 0)  #plotagem e condicoes
        
    plt.title((str(nome_posto) + '\nChuva-Vazao'), size = 15)
    
    ax2.set_ylabel('Precipitacao (mm)', color='r', size = 15)  ##colocacao e condicoes do segundo eixo y
    for corlabel2 in ax2.get_yticklabels():         #trocar a cor dos valores do segundo eixo y
        corlabel2.set_color('r')

    ax2.yaxis.set_ticks(grid2)  #grid
    ax2.grid(True)  #Ligar/Desligar o grid
        #Ate aqui
        
        #salve o grafico
    plt.savefig(str(caminho_saida) + "/PlotagensPQ/Operacao_" + str(numero_do_grafico) + '_Chuva-Vazao.png')  #salvar imagem do grafico

#----------------------------- SEGUNDA FIGURA COMECA A PARTIR DAQUI ------------------------    

    fig = plt.figure(figsize=(15,9), dpi=60)
    ax3 = fig.add_axes([0.126, 0.1, 0.772, 0.8])
    
    plt.axis([0, nint_tempo, 0, (altura_maxima_grafico) ])  #declarar eixos
    
        #plotagem da linha (Hidrograma)
    ax3.plot(x, Hidrograma, 'b-', linewidth=4, label = 'Vazao de entrada')
    
            #Determinar volume de chuva atraves do metodo dos retângulos  
    volume = 0.0
    for vol in xrange(0,(len(Hidrograma)-1)):
        volume = (volume + ((Hidrograma[vol+1] + Hidrograma[vol])/2.))  
          
    volume = volume * dt # volume e' m3... hidrograma esta' em m3/intervalo de tempo (segundos)
    coef_escoam = (sum(Pef)/sum(Pord))    
    
        #Anotacoes
    plt.annotate('Vazao de Pico   = %13.6f m3/s' %(max(Hidrograma)), xy = ((0.65*nint_tempo),(max(Hidrograma)*1.1)),  xycoords='data', xytext=None, color = 'b' ,textcoords=None)#"Tabelinha"   
    plt.annotate('Vol. Escoado     = %13.4f m3' %(volume), xy = ((0.65*nint_tempo),(max(Hidrograma)*1)),  xycoords='data', xytext=None, color = 'b' ,textcoords=None)#"Tabelinha"
    plt.annotate('Coef. Escoame. = %13.6f' %(coef_escoam), xy = ((0.65*nint_tempo),(max(Hidrograma)*0.9)),  xycoords='data', xytext=None, color = 'b' ,textcoords=None)#"Tabelinha"
    
        #Nomear eixos
    ax3.set_xlabel('Intervalos de tempo', size = 15)   #nome do eixo x
    ax3.set_ylabel('Vazao (m3/s)', color='b', size = 15)       #nome e cor do nome do eixo y         
    for corlabel1 in ax3.get_yticklabels():         #trocar a cor dos valores do eixo y
        corlabel1.set_color('b')
    
    ax3.yaxis.set_ticks(grid_horizontal_1) #Dizer quais valores serem mostrados no primeiro eixo Y
            
    ax4 = ax3.twinx() #inverter o segundo eixo y
    
        #Determinar eixos
    plt.ylim( (max(Pord)*3),0)  #fica como deve ser, mas em tamanho de todo grafico    
    plt.xticks(grid_vertical) #Dizer quais valores serem mostrados no eixo X
    plt.yticks(grid2) #Dizer quais valores serem mostrados no segundo eixo Y
    
    
        #Plotagem das barras
    plt.bar(segundo_eixo_x, Pord, width = 1, color='r', linewidth = 0, label = "Precipitacao")  #plotagem e condicoes        
    plt.bar(terceiro_eixo_x, Pef, width = 1, color='cyan', linewidth = 0, label = "Prec. Efetiva")  #plotagem e condicoes    
            
    ax4.set_ylabel('Precipitacao e precipitacao efetiva (mm)', color='r', size = 15)  ##colocacao e condicoes do segundo eixo y
    for corlabel2 in ax4.get_yticklabels():         #trocar a cor dos valores do segundo eixo y
        corlabel2.set_color('r')
        
    plt.title((str(nome_posto) + '\nComparacao'), size = 15)
    
    plt.legend(loc='upper right')
                  
    plt.savefig(str(caminho_saida) + "/PlotagensPQ/Operacao_" + str(numero_do_grafico) + '_Comparacao.png')  #salvar imagem do grafico
    
    fig.clf('all') #nao armazenar os graficos na memoria
    plt.close('all') #fechar as figuras pra nao armazenar na memoria
    
#_______________________________________________________________________# 
#Plotagem dos Cenarios de IDF
def plotar_Cenarios_PQ(hidrogramas, cenarios_anos, numero_intervalos_tempo, caminho_saida, nome_posto, numero_do_grafico):
    """
    Funcao responsavel por plotar e salvar N cenarios de determinado posto de chuva para os tempos de retorno indicados no arquivo de entrada.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        
            hidrogramas: Lista que contem os dados dos hidrogramas a serem plotados.
                -> Esta variavel deve ser estruturada da seguinte forma:
                hidrogramas = [ [...], [...], [...], ... ] -> Cada bloco [...] possui a informacao de um hidrograma [em metros^3/s].
                
            cenarios_anos: Lista que contem os anos correspondente a cada hidrograma de entrada.
                -> Esta variavel deve ser estruturada da seguinte forma:
                cenarios_anos = [...] -> Anos dos hidrogramas de entrada respectivamente.
            
            numero_intervalos_tempo: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            
            caminho_saida: Variavel do tipo string que armazena o diretorio em que a imagem sera' salva.
            
            nome_posto: Variavel do tipo string que armazena o titulo do grafico.
            
            numero_do_grafico: Variavel do tipo inteira que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
                -> OBS: Esta variavel deve assumir um valor diferente para cada plotagem. 
                        E' recomendado utilizar o numero da operacao como valor para numero_do_grafico.
                        O nome final do arquivo e': (caminho_saida)/PlotagensCENARIOS/Operacao_(numero_do_grafico)_Puls.png
            
    """
    
    ######################################## --- ATENCAO!!! --- ##############################################
    #                                                                                                        #
    #       Esta funcao nao funciona quando os valores de vazao gerados pela simulacao de chuva-vazao        #
    #   sao muito pequenos, logo, deve-se adicionar a restricao de plotagem desses graficos se os valores    #
    #   dos hidrogramas de projeto (QUALQUER UM DELES) forem muito pequenos.                                 #
    #                                                                                                        #
#####################################################################################################################################
#    
#    #Segue o erro:
#    
#Exception in Tkinter callback
#Traceback (most recent call last):
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\App\appdata\canopy-1.5.1.2730.win-x86_64\lib\lib-tk\Tkinter.py", line 1470, in __call__
#    return self.func(*args)
#  File "D:\Documentos\Arquivos_PYTHON\Hydrolib\Modelo Ecotecnologias\2015_11_22\MHE_20151122.py", line 74, in buscarArquivoEntrada
#    self.lerArquivoEntrada()
#  File "D:\Documentos\Arquivos_PYTHON\Hydrolib\Modelo Ecotecnologias\2015_11_22\MHE_20151122.py", line 623, in lerArquivoEntrada
#    (operacao+1)                                  )
#  File "D:\Documentos\Arquivos_PYTHON\Hydrolib\Modelo Ecotecnologias\2015_11_22\Hydrolib.py", line 600, in Plotagem_Cenarios_PQ
#    plt.savefig(str(caminho_saida) + '/PlotagensCENARIOS/Operacao_' + str(numero_do_grafico) + '_Comparacao.png')  #salvar imagem do grafico
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\pyplot.py", line 577, in savefig
#    res = fig.savefig(*args, **kwargs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\figure.py", line 1470, in savefig
#    self.canvas.print_figure(*args, **kwargs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\backends\backend_qt5agg.py", line 161, in print_figure
#    FigureCanvasAgg.print_figure(self, *args, **kwargs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\backend_bases.py", line 2194, in print_figure
#    **kwargs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\backends\backend_agg.py", line 521, in print_png
#    FigureCanvasAgg.draw(self)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\backends\backend_agg.py", line 469, in draw
#    self.figure.draw(self.renderer)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\artist.py", line 59, in draw_wrapper
#    draw(artist, renderer, *args, **kwargs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\figure.py", line 1079, in draw
#    func(*args)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\artist.py", line 59, in draw_wrapper
#    draw(artist, renderer, *args, **kwargs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\axes\_base.py", line 2092, in draw
#    a.draw(renderer)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\artist.py", line 59, in draw_wrapper
#    draw(artist, renderer, *args, **kwargs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\axis.py", line 1114, in draw
#    ticks_to_draw = self._update_ticks(renderer)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\axis.py", line 957, in _update_ticks
#    tick_tups = [t for t in self.iter_ticks()]
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\axis.py", line 903, in iter_ticks
#    self.major.formatter.set_locs(majorLocs)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\ticker.py", line 523, in set_locs
#    self._set_format(vmin, vmax)
#  File "C:\Users\Vitor\AppData\Local\Enthought\Canopy\User\lib\site-packages\matplotlib\ticker.py", line 584, in _set_format
#    loc_range_oom = int(math.floor(math.log10(loc_range)))
#ValueError: math domain error
#####################################################################################################################################    
    
    #Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    import os
    from numpy import array, linspace
    
    
            #Agora que eu deletei a pasta antiga, faca uma nova para salvar os graficos 
    if not os.path.exists(caminho_saida + "/PlotagensCENARIOS"):
        os.makedirs(caminho_saida + "/PlotagensCENARIOS")
        
        #funcao max() nao esta' funcionando.... achar o valor maximo manualmente....
    altura_maxima_grafico = 0
    
    for i in hidrogramas: #i assume os valores de cada sublista
        for i2 in xrange(len(i)): #dentro de cada sublista, ver item a item
            if i[i2] >= altura_maxima_grafico: #condicional
                altura_maxima_grafico = i[i2] #armazene
                
    altura_maxima_grafico = int(1.3*altura_maxima_grafico)
    
    fig = plt.figure(figsize=(15,9), dpi=60)    #inicio da primeira plotagem
    ax1 = fig.add_axes([0.126, 0.1, 0.772, 0.8]) #ajustar a tela
    
    grid_horizontal_1 = linspace((0),(altura_maxima_grafico),(5)) #grid horizontal (eixo y)
    grid_vertical = linspace((0),( numero_intervalos_tempo ),(5)) #grid vertical (eixo y)
    
    ax1.xaxis.set_ticks(grid_vertical) #nomear grid
    ax1.yaxis.set_ticks(grid_horizontal_1) #nomear grid
    ax1.grid(True) #Ligar/Desligar o grid
    
    x = array([i for i in xrange( numero_intervalos_tempo )])  #transforma eixo x em array (primeira plotagem)

    plt.axis([0, numero_intervalos_tempo, 0, (altura_maxima_grafico) ])  #declarar eixos
    
    for plotar in xrange(1, (len(hidrogramas)+1) ):
        ax1.plot(x, hidrogramas[-plotar], linewidth=4, label = str(cenarios_anos[-plotar]) +' anos')  #plotagem
        
    ax1.set_xlabel('Intervalos de tempo', size = 15)   #nome do eixo x
    ax1.set_ylabel('Vazao (m3/s)', color='b', size = 15)       #nome e cor do nome do eixo y         
    for corlabel1 in ax1.get_yticklabels():         #trocar a cor dos valores do eixo y
        corlabel1.set_color('b')

    plt.title((str(nome_posto) + '\nCenarios'), size = 15) 

    plt.legend(loc='upper right')
    
    plt.savefig(str(caminho_saida) + '/PlotagensCENARIOS/Operacao_' + str(numero_do_grafico) + '_Comparacao.png')  #salvar imagem do grafico

    fig.clf('all') #nao armazenar os graficos na memoria
    plt.close('all') #fechar as figuras pra nao armazenar na memoria
    
#_______________________________________________________________________#

#Vazao de referência
  
#def vazao_referencia(I,dt,S,n,B):
#    
#    #Algoritmo original escrito por Lucas Tassinari, correcoes e otimizacoes sao necessarias...
#    
##    conforme Tucci (2005) pagina 465 - Hidrologia Cienia e aplicacao, quarta edicao
#    
#    import matplotlib.pyplot as plt
#    import numpy as np
#    
#    
#    Q_ref = 0.7*max(I)                                  #Vazao de referência e 70% da vazao maxima de entrada, conforme Tucci (1998) apud Collischon e Dornelles (2013)
#    
#    c = 5/3.0*S**0.3*Q_ref**0.4/(n**0.6*B**0.4)         #Nessa equacao ha uma simplificacao que considera o rio largo.
#                                                        #Celeridade, conforme Tucci (2005) pagina 164 - Modelos Hidrologicos      ####
#
#    dT = dt*60.0                                        #Tempo (em horas) - VITOR: AQUI e' em SEGUNDOS!!!!
#    
#        #Espacamento - limite superior
#    dx = c*dT/2*(1+(1+1.5*Q_ref/(B*S*dT*c**2))**0.5)    #Este e o limite superior de dx. Assim, dx pode assumir valores menores do que o calculado
#                                                        #Essa equacao foi apresentada por Fread (1993) apud Collischon e Dornelles (2013).
#                                                        #CONFERIR COM O DANIEL SE PODEMOS UTILIZAR ESTA EQUAcaO
#                                                     
#    N = comprimento_rio//dx+1                           #Definicao do número de trechos
#    dX = comprimento_rio/N  
#    X = 0.5*(1-Q_ref/(B*S*c*dX))                        #Parâmetro X (número de trechos)
#    K = dX/c#
#
#        #Verificacões - MONTAR ALGO QUE AVISE SE V2 NaO ESTa ENTRE V1 E V3 -- ##
#
#    v1 = X; v2 = dT/(2*K); v3 = (1-X)    
#    C1 = (dT-2*K*X)/(2*K*(1-X)+dT)                      #Verificacoes - Definicao parâmetro C1
#    C2 = (dT+2*K*X)/(2*K*(1-X)+dT)                      #Verificacoes - Definicao parâmetro C2
#    C3 = (2*K*(1-X)-dT)/(2*K*(1-X)+dT)                  #Verificacoes - Definicao parâmetro C3
#    
#        #Saida da propagacao - Q
#
#    Q = np.empty (len(I))                               #Define o array vazio
#    I_inicial = I                                       #Saida da propagacao - I_inicial
#    for m in xrange (int(N)):
#        for i in xrange (1,len(I)):
#            Q[0] = I[0]                                 #Considera-se que a Vazao Inicial de saida e igual a Vazao Inicial de Entrada
#            Q[i] = C1*I[i] + C2*I[i-1] + C3*Q[i-1]
#        I=np.array([Q[i] for i in xrange (0,len(I),1)])  #A translacao da vazao deve ser feita com essa linha, se nao, nao da certo.#
#
#        #Plotagem 2
#
#    
#        #Preparar eixos:
##    eixo_x = np.array([[i] for i in xrange( 0,len(vazao_entrada_propagacao),1 ) ])
#    
#    fig = plt.figure(figsize=(15,9), dpi=60)
#    ax5 = fig.add_axes([0.126, 0.1, 0.772, 0.8])
#    
##    plt.axis([min(eixo_x), max(eixo_x), 0, (1.25*(max(I_inicial))) ])  #declarar eixos
#    
##    l1 = ax5.plot( eixo_x, I_inicial, 'r-', linewidth=4, label = 'Vazao de entrada')
##    l2 = ax5.plot( eixo_x, Q, 'g-', linewidth=4, label = 'Vazao de saida' )#
#
#    ax5.set_xlabel('Tempo (Unidades de tempo)', size = 15)
#    ax5.set_ylabel('Vazao (m3/s)', size = 15)
#    ax5.grid(True)
#    
#    plt.legend()    #
#
##_______________________________________________________________________#   

def calcular_VazaoSaida_Puls(ESTRUTURAS, CURVA_COTA):
    """
    Esta funcao e' responsavel por calcular a curva de extravasao de um reservatorio a partir de suas estruturas.
        
    Ela retorna uma lista com as vazoes de saida calculada para 101 pontos entre a menor e a maior cota.
        curva_de_vazao = [...]
                        
    Parametros para uso:
        
            ESTRUTURAS: Lista que contem a informacao necessaria para calcular a vazao extravasada por cada estrutura.
                -> Esta variavel e' estruturada da seguinte forma:
                ESTRUTURAS = [ [...], [...], [...], ...] -> cada bloco [...] contem a informacao de uma estrutura (nao ha' limite de estruturas), que podem ser:
                    1 - Vertedor: ["VERTEDOR", 1.5, 10, 30, 25] -> String informando o tipo da estrutura, coeficiente C da estrutura, comprimento de soleira (m),
                    cota maxima do vertedor (m) e cota de soleira do vertedor (m).
                    2 - Orificio: ["ORIFICIO", 1.5, 7.069, 1.5, 20] -> String informando o tipo da estrutura, coeficiente C da estrutura, area do orificio (m2), 
                    altura/diametro do orificio (m) e cota do centro do orificio (m).
                -> OBS: A string usada para indicar o nome da estrutura deve ser escrita toda em maiuscula e sem acentos: "VERTEDOR" ou "ORIFICIO"
            
            CURVA_COTA: Lista que contem a informacao de cota da curva cota-volume.
                -> Esta variavel e' estruturada da seguinte forma:
                CURVA_COTA = [ ...... ] -> Uma lista que contem os valores de cota (m).
                -> OBS: OS VALORES DE COTA DEVEM ESTAR ORDENADOS DE FORMA CRESCENTE (do menor ao maior).
                
    """
    
    from tkMessageBox import showinfo
    import sys
#    from numpy import linspace, array
#    from numpy import array
    from math import acos, sin


    #Algoritmo original escrito por Vitor Geller.
    

    
#    #   cota_inicio_extravasao recebe o menor valor de cota das estruturas do reservatorio
#    cota_inicio_extravasao        = min(cotas_estruturas)
#    indice_cota_inicio_extravasao = cotas_estruturas.index(cota_inicio_extravasao) #estou vendo qual e' a posicao desta menor cota, pois e' preciso avaliar se ela pertence a um orificio
#    
#    #   Loop para verificar se a estrutura com menor cota e' um orificio: Isto e' necessario pois o orificio comeca a gerar vazoes com niveis de agua menores que sua cota (que e' medida no centro do orificio)
#    if (ESTRUTURAS[indice_cota_inicio_extravasao][0] == "ORIFICIO"):
#        cota_inicio_extravasao -= (ESTRUTURAS[indice_cota_inicio_extravasao][3]/2.)  #isto significa: cota do orificio - seu raio.


####    alturas_calculadas   = linspace(CURVA_COTA[0],CURVA_COTA[-1],101)      #da menor cota ate' a maior: colocar 100 valores intermediarios.

    #   Evitar erros grosseiros
    if (not CURVA_COTA[0] == min(CURVA_COTA)):
        showinfo("Erro.", "A cota do fundo do reservatório (primeira cota do arquivo) deve ser menor que as demais cotas informadas na curva cota-volume.\nVerifique o arquivo de entrada.") #"Voce e' burro." ahahhahahaha
        sys.exit()
    
    #   Se nenhum erro grosseiro foi detectado, rode o algoritmo
    else:
        
        #   cotas_estruturas recebe as cotas das estruturas de extravasao existentes
        cotas_estruturas = [] #declarar a lista
        
        #   Loop para reunir as informacoes de cota de cada estrutura
        for estrutura in ESTRUTURAS:
            #   Se for orificio...
            if estrutura[0] == "ORIFICIO":
                cotas_estruturas.append(estrutura[4] - (estrutura[3]/2.)) #cota do centro do orificio - raio 
            #   Se for vertedor...
            elif estrutura[0] == "VERTEDOR":
                cotas_estruturas.append(estrutura[4]) # se for vertedor e' so' adicionar
        
#        alturas_calculadas   = linspace(min(cotas_estruturas), CURVA_COTA[-1], 101)        #da menor cota ate' a maior: colocar 100 valores intermediarios.
        incremento_de_altura = ( (CURVA_COTA[-1] - min(cotas_estruturas)) /100.)            #vai ter 101 valores + o numero de cotas
#        alturas_calculadas   = array([0. for alt in xrange(101 + len(cotas_estruturas))])  #101 valores + valores de cota das estruturas...
#        alturas_calculadas   = [0. for alt in xrange(101 + len(cotas_estruturas))]         #101 valores + valores de cota das estruturas...
        alturas_calculadas   = [0. for alt in xrange(100 + len(cotas_estruturas))]         #101 valores + valores de cota das estruturas...
#        curva_de_vazao       = array([0. for vaz in xrange(len(alturas_calculadas))])      #cria uma variavel de 0's. 101 valores, um para cada ponto que sera' calculada
        curva_de_vazao       = [0. for vaz in xrange(len(alturas_calculadas))]             #cria uma variavel de 0's. 101 valores, um para cada ponto que sera' calculada
        
        #   Loop para preencher os valores de altura:
        for contadora in xrange(len(alturas_calculadas)):
            #   Valor da altura e' = min(cotas_estruturas) + contadora*incrementos
            alturas_calculadas[contadora] = (min(cotas_estruturas) + (contadora * incremento_de_altura))
            
        #   Loop para substituir os valores finais por valores de interesse
        for contadora in xrange(1, (len(cotas_estruturas))):
            #   Checar se a cota da estrutura ja' nao esta' dentro da lista de cotas...
            if (not cotas_estruturas[-contadora] in alturas_calculadas):
                #   Substituir os valores de atras para frente para rearanja-los
                alturas_calculadas[-contadora] = cotas_estruturas[-contadora]
            
        #   Ordena-se as alturas em ordem crescente!
        alturas_calculadas.sort() 
        
        
########        incremento_de_altura = (alturas_calculadas[1] - alturas_calculadas[0]) #serve para controlar o 'passo' de cada ponto a ser calculado
####        nivel_dagua          = (CURVA_COTA[0] - incremento_de_altura)          #comeco o calculo do fundo do reservatorio - incremento_de_altura pois a parcela e' somada no primeiro loop antes de comecar os calculos
########        nivel_dagua          = (COTA_FUNDO - incremento_de_altura)         #comeco o calculo do fundo do reservatorio - incremento_de_altura pois a parcela e' somada no primeiro loop antes de comecar os calculos
        
    
    
    #### Adicionado para checar a correcao #### INICIO
##    zero = 0.0
##    print " numLoop,   curva_vazao = coeficiente * comprimento *  carga d'agua + (nivel_atual)"
    #### Adicionado para checar a correcao #### FIM
    
    
            #Criar a curva de saida de vazao
        numero_loop = -1 #Decidi fazer assim o for a seguir fica mais limpo. Esta variavel e' usada pra indicar o indice do resultado calculado. Ele comeca em -1 pois e' somado 1 a cada loop
        vazao_nivel_qualquer = 0.                                              #variavel usada para armazenar a vazao de cada ponto analizado.
        
        #   Loop dos niveis de agua
        for cota_da_agua in alturas_calculadas:        #variando do inicio da curva cota-volume ate' o final dela.
            
            numero_loop += 1                        #somar um loop
            vazao_nivel_qualquer = 0.               #resetar a variavel em cada novo nivel analisado
            
########            nivel_dagua += (incremento_de_altura) #acrescentar incremento_de_altura para cada loop... comeca na menor cota pois ja' foi descontado incremento anteriormente
            
########            for estrutura in xrange(len(ESTRUTURAS)): #analisando todas as estruturas com um certo nivel de agua.

            #   Loop das estruturas
            for estrutura in ESTRUTURAS: #analisando todas as estruturas com um certo nivel de agua.  
                              
                #    Ver se as estruturas possuem carga de agua
                if (estrutura[4] < (cota_da_agua)):  #se a cota da estrutura que estou analisando for menor que o nivel da agua, ele entra no calculo de vazao
                    
                    #    Se for vertedor com carga
                    if ( estrutura[0] == "VERTEDOR" ): #Q = C*L*(h**1.5), p. 400, HIDRAULICA BASICA, 3 ed. RODRIGO DE MELO PORTO
                        vazao_nivel_qualquer += ( float(estrutura[1]) * float(estrutura[2]) * (( cota_da_agua - float(estrutura[4]) )**(1.5)) )
                    
                    #    Se for orificio com carga
                    elif ( estrutura[0] == "ORIFICIO" ):  #ver se ele esta' afogado ou nao
                        
                        #    Se entrar no if, nao esta' afogado ainda.
                        if ((cota_da_agua) < (estrutura[4] + (estrutura[3]/2.))): # (cota do centro + meio diametro/altura) ... orificio ainda nao esta' afogado, usar manning
                            
                                #EQUACOES RETIRADAS DO LIVRO HIDRAULICA BASICA, p. 256 e 257, 3ed., RODRIGO DE MELO PORTO
                            yo = (cota_da_agua - ( float(estrutura[4]) - (float(estrutura[3])/2.) ))                         #altura do fundo do orificio ate' o nivel dagua
                            theta = 2 * acos(1 - 2*yo/ float(estrutura[3]) )                                                 #theta = 2arccos(1 - 2 *yo/diametro)
                            raio_hidraulico = ( float(estrutura[3]) * (( 1 - (sin(theta)/theta) )/4.) )                      #Rh = (diametro * (1 - (sen(theta)/theta))/4)
                            area_molhada = ( (float(estrutura[3])**2) * ((theta - sin(theta))/8.) )                          #A = (D**2 * (theta - sen(theta))/8)
                            declividade = 0.0010                                                                             #m/m adotado
                            coef_rugosidade = 0.013                                                                          #Superfícies de argamassa de cimento em condicoes regulares, 
                                                                                                                             #p. 273, HIDRAULICA BASICA, 3 ed. RODRIGO DE MELO PORTO
                            #    equacao de manning  - Q = 1/n * A * Rh**(2/3) * Io**(0.5)
                            vazao_nivel_qualquer += ( area_molhada * (raio_hidraulico**(2/3.)) * (declividade**(0.5)) / coef_rugosidade ) #p. 244, HIDRAULICA BASICA, 3 ed. RODRIGO DE MELO PORTO
                        
                        else: #    Se entrar no else, esta' afogado.
                            #    Q = C*Ao*((2*G*H)**0.5), p. 370, HIDRAULICA BASICA, 3ed. RODRIGO DE MELO PORTO
                            vazao_nivel_qualquer += ( float(estrutura[1]) * float(estrutura[2]) * ( (2. * 9.81 * (cota_da_agua - float(estrutura[4])))**0.5 ) )
                        
                    #    estrutura nao identificada, verifique o arquivo de entrada
                    else:
                        showinfo("Erro.", "Estrutura de extravasão não reconhecida: %s \nVerifique o arquivo de entrada." %(estrutura[0])) #"Voce e' burro." ahahhahahaha
                        sys.exit()
                        
                #    Ou seja, estrutura[4] <= cota_da_agua -> cota da estrutura e' menor ou igual a cota da agua
                else: 
                                        
                    #    Somente orificio e' calculado, pois vertedor nao gera vazao se o nivel de agua nao atingiu a cota de soleira.
                    if ( estrutura[0] == "ORIFICIO" ): #orificio com pouco nivel de agua -> calcular a vazao pela equacao de manning
                            
                        #    EQUACOES RETIRADAS DO LIVRO HIDRAULICA BASICA, p. 256 e 257, 3ed., RODRIGO DE MELO PORTO
                        yo = ( (float(estrutura[3])/2.) - (float(estrutura[4]) - cota_da_agua) )                             #altura do fundo do orificio ate' o nivel dagua
                        
                        #   Este loop serve para que nao ocorra divisao por zero, pois se yo = 0, theta = 0 e no calculo do raio hidraulico resulta em divisao por zero.
                        if (not yo <= 0):   #   pois yo < 0 e' possivel. Isto ocorre quando o nivel esta' tao abaixo que sequer esta' encostando na estrutura de extravasao
                            
                            theta = 2 * acos(1 - 2*yo/ float(estrutura[3]) )                                                 #theta = 2arccos(1 - 2 *yo/diametro)
                            raio_hidraulico = ( float(estrutura[3]) * (( 1 - (sin(theta)/theta) )/4.) )                      #Rh = (diametro * (1 - (sen(theta)/theta))/4)
                            area_molhada = ( (float(estrutura[3])**2) * ((theta - sin(theta))/8.) )                          #A = (D**2 * (theta - sen(theta))/8)
                            declividade = 0.0010                                                                             #m/m adotado
                            coef_rugosidade = 0.013                                                                          #Superfícies de argamassa de cimento em condicoes regulares, 
                                                                                                                             #p. 273, HIDRAULICA BASICA, 3 ed. RODRIGO DE MELO PORTO
                            #    equacao de manning  - Q = 1/n * A * Rh**(2/3) * Io**(0.5)
                            vazao_nivel_qualquer += ( area_molhada * (raio_hidraulico**(2/3.)) * (declividade**(0.5)) / coef_rugosidade ) #p. 244, HIDRAULICA BASICA, 3 ed. RODRIGO DE MELO PORTO
                        
                        #   ou seja, yo <= 0
                        else:
                            vazao_nivel_qualquer += 0. #vazao inalterada.
                            
                    #    estrutura nao identificada, verifique o arquivo de entrada
                    elif ( (not estrutura[0] == "ORIFICIO") and (not estrutura[0] == "VERTEDOR") ): 
                        showinfo("Erro.", "Estrutura de extravasão não reconhecida: %s \nVerifique o arquivo de entrada e execute o modelo novamente." %(estrutura[0])) #"Voce e' burro." ahahhahahaha
                        sys.exit()
                        
    ##                print " %7d, %11.6f = %11.6f * %11.6f * %11.6f , (%11.6f)" %(num_incremento, curva_de_vazao[num_incremento], ESTRUTURAS[0][1], ESTRUTURAS[0][2], (zero), nivel_dagua )
                    
                #feito a verificacao de todas as estruturas, posso armazenar o valor de vazao encontrado e calcular o proximo ponto.
            curva_de_vazao[numero_loop] = vazao_nivel_qualquer #armazeno o valor de vazao calculado
            #### Adicionado para checar a correcao #### INICIO
    ##        print " %7d, %11.6f = %11.6f * %11.6f * %11.6f , (%11.6f)" %(num_incremento, curva_de_vazao[num_incremento], ESTRUTURAS[0][1], ESTRUTURAS[0][2], ((nivel_dagua - float(ESTRUTURAS[0][4]) )**(1.5)), nivel_dagua )
            #### Adicionado para checar a correcao #### FIM
                    
        return curva_de_vazao, alturas_calculadas
    
#_______________________________________________________________________#   

#Aplicacao do metodo de Puls Modificado
   
def aplicar_Puls(CURVA_COTA_VOLUME, HIDROGRAMA_ENTRADA_PULS, CURVA_VAZOES, ALTURAS_VAZOES_CALCULADAS, COTA_INICIAL, NUMERO_INTERVALOS_TEMPO, DURACAO_INTERVALO_TEMPO):
    """
    E' a funcao responsavel por calcular o hidrograma de saida de um reservatorio. 
    
    A funcao retorna uma variavel do tipo lista que contem os valores do hidrograma de saida do reservatorio [m³/s].
        HIDROGRAMA_SAIDA = [...] 
    
    Parametros para uso:
        
            CURVA_COTA_VOLUME: Lista que contem a informacao da curva cota-volume do reservatorio.
                -> Esta variavel deve ser estruturada da seguinte forma:
                CURVA_COTA_VOLUME = [ [...], [...] ] -> Em que o primeiro bloco [...] contem somente dados de cota [em metros], e o segundo bloco [...] contem somente 
                dados de volume [10^6 metros³].
                
            HIDROGRAMA_ENTRADA_PULS: Lista que contem os dados do hidrograma de entrada do reservatorio.
                -> Esta variavel deve ser estruturada da seguinte forma:
                HIDROGRAMA_ENTRADA_PULS = [...] -> Dados de entrada de vazao [em metros^3/s].
                
            CURVA_VAZOES: Lista que contem os dados de extravasao do reservatorio.
                -> Esta variavel deve ser estruturada da seguinte forma:
                CURVA_VAZOES = [...] -> Dados de saida de vazao [em metros^3/s].
            
            ALTURAS_VAZOES_CALCULADAS:

             
            ->>>>>>> corrigir COTA_INICIAL: Variavel do tipo inteiro que armazena a cota inicial do reservatorio.
            
            NUMERO_INTERVALOS_TEMPO: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            
            DURACAO_INTERVALO_TEMPO: Variavel do tipo inteiro que armazena a duracao do intervalo de tempo [em segundos].
    """
    
    #Algoritmo original escrito por Vitor Geller. Otimizacoes sao necessarias
    
    from tkMessageBox import showinfo
    import sys
    from numpy import linspace
    from scipy.interpolate import interp1d
  
  
  ######################### ERRO ENCONTRADO:
  # NAO PODE-SE FAZER INTERP PRA COTA-VOLUME, POIS ASSIM, ASSUME-SE QUE O RESERVATORIO E' LINEAR, QUANDO ELE NAO E'. POR ISSO, DEVE-SE RESOLVER A INTERPOLACAO NA MAO
  # REVER A LINHA 1115 ->     interp_cota_volume = interp1d(cotas_interpoladas, volumes_calculados)     #RELACIONANDO COTA COM VOLUME. Entra cota, sai volume.  
  
        ###***--- INTERPOLAR AS CURVAS (COTA, VOLUME E VAZAO) ---***###

        #'quebrar' os valores de cota em 101 valores
####    cotas_interpoladas = linspace(CURVA_COTA_VOLUME[0][0],CURVA_COTA_VOLUME[0][-1],101) #criar variavel que possui o mesmo numero de termos que a curva de saida de vazao -> fazer interpolacao
    cotas_interpoladas = linspace(CURVA_COTA_VOLUME[0][0], CURVA_COTA_VOLUME[0][-1], 101) #criar variavel que possui o mesmo numero de termos que a curva de saida de vazao -> fazer interpolacao
#    volumes_calculados = linspace(CURVA_COTA_VOLUME[1][0], CURVA_COTA_VOLUME[1][-1], 101)
#    alturas_com_vazoes = linspace(ALTURAS_CALCULADAS_VAZOES, CURVA_COTA_VOLUME[0][-1], 101)  #deve ser diferente pois a cota de extravasao geralmente e' maior que a cota de fundo.
    
        #FORMULAS DE CORRELACAO PARA POSTERIOR INTERPOLACAO
####    interp_cota_volume = interp1d(CURVA_COTA_VOLUME[0], CURVA_COTA_VOLUME[1]) #RELACIONANDO COTA COM VOLUME. Entra cota, sai volume.
#    interp_cota_volume = interp1d(cotas_interpoladas, volumes_calculados)     #RELACIONANDO COTA COM VOLUME. Entra cota, sai volume.

    interp_cota_volume = interp1d(CURVA_COTA_VOLUME[0],CURVA_COTA_VOLUME[1])   #cria a funcao interpolacao dos valores brutos, será substituida a seguir...
    interp_cota_vazao  = interp1d(ALTURAS_VAZOES_CALCULADAS, CURVA_VAZOES)     #RELACIONANDO cotas COM VAZAO DE SAIDA. Entra cota, sai vazao de saida.
    
#    volumes_calculados = [0 for i in xrange(101)]    
#    #   Loop para fazer determinar os valores interpolados de vazao para as alturas calculadas
#    for altura in xrange(len(cotas_interpoladas)):
#        volumes_calculados[altura] = interp_cota_volume(cotas_interpoladas[altura])
        
    ######################################################## LEIA ATENTAMENTE ANTES DE SEGUIR ##############################################################
    #                                                                                                                                                      #
    #       -> O algoritmo a seguir divide a variavel SdtQ (2*S/dt [m³/s] + Q [m³/s]) em duas parcelas, SdtQ1 e SdtQ2.                                     #
    #                                                                                                                                                      #
    #       -> A primeira delas (SdtQ1) e' feita para cotas entre o fundo do reservatorio e a cota que a primeira estrutura (com menor cota) de extravasao #
    #        comeca a funcionar. Portanto os valores de SdtQ1 sao obtidos somente com o armazenamento (a parcela Q e' sempre nula).                        #
    #                                                                                                                                                      #
    #       -> A segunda delas (SdtQ2) e' feita para as mesmas cotas usadas para montar a curva de extravasao, pois esta variavel possui os dois termos da #
    #       soma diferentes de zero (2*S/dt e Q). Diferentemente do que voce pode estar pensando, e' necessario usar as mesmas cotas na obtencao desta va- #
    #       riavel pois assim ficam demarcadas na curva os pontos (cotas) em que uma nova estrutura comeca a extravasar, evitando o erro demonstrado a se- #
    #       guir:                                                                                                                                          #
    #           Imagine que temos uma estrutura de extravasao na cota 120 metros.                                                                          #
    #           A cota do reservatorio na iteracao N foi calculada em 119.95 metros.                                                                       #
    #                                                                                                                                                      #
    #              Cota, Volume, Vazoes,    -> Como a estrutura de extravasao esta' na cota 120 m, a vazao de saida para cotas < 120 m e' zero. Porem,     #
    #            119.70,  21.02,      0,    -> Se calcularmos a vazao na cota 119.95 m obteremos um valor de vazao diferente de zero, ja' que o inter-     #
    #            120.20,  21.60,   2.15,    pretador nao sabe que a vazao ate' a cota 120 m e' zero. Ja' se utilizamos as mesmas cotas que foram uti-      #
    #            120.70,  21.96,   5.21,    lizadas para construcao da curva de vazoes, o interpretador tera' as informacoes necessarias para interpo-     #
    #                                       lar corretamente (informacoes estas que estao faltando neste exemplo, que sao cota 120 = vazao 0 ).            #
    #                                                                                                                                                      #
    ########################################################################################################################################################
    
        #Montar a parcela 2*S/dt + Q [m³/s]
    SdtQ1 = [0. for i in xrange(len(cotas_interpoladas))]        #101 valores porque eu quis
    SdtQ2 = [0. for i in xrange(len(ALTURAS_VAZOES_CALCULADAS))] #
    cotasSdtQ1 = linspace(CURVA_COTA_VOLUME[0][0], min(ALTURAS_VAZOES_CALCULADAS), 101) #alturas usadas no calculo de SdtQ1
    
    #   Loop para montar SdtQ1. Ele e' construido so' para cotas entre o menor valor de cota e o menor valor de altura das vazoes
    for contador in xrange(len(cotas_interpoladas)):
        #   Determinar o volume armazenado em uma cota qualquer compreendida entre min(cota volume) e min(altura_vazoes_calculadas)
        volume_armazenado = interp_cota_volume(cotasSdtQ1[contador])
        #   Calcular SdtQ1[contador]
        SdtQ1[contador] = (float(2*volume_armazenado*(10**6))/DURACAO_INTERVALO_TEMPO)
        
#    print "alturas_vazoes_calculadas = " + str(ALTURAS_VAZOES_CALCULADAS)
    
    #   Loop para montar a SdtQ2. Ela e' construida para valores de cota da variavel ALTURAS_VAZOES_CALCULADAS, pois somente esta variavel possui os valores chave necessarios para correta interpolacao em determinadas cotas.
    for contador in xrange(len(ALTURAS_VAZOES_CALCULADAS)):
        #   Determinar o volume armazenado nas cotas das ALTURAS_VAZOES_CALCULADAS (cotas usadas no calculo da curva de vazao)
        volume_armazenado = interp_cota_volume(ALTURAS_VAZOES_CALCULADAS[contador])
        #   Determinar a vazao de saida do reservatorio. Esta linha nao precisa ser assim, uma vez que os valores que serao interpolados sao os mesmos que sao usados para montar a curva. Pode ser substituido por curva_vazao[contador]
        vazao_cota_qualquer = interp_cota_vazao(ALTURAS_VAZOES_CALCULADAS[contador]) #pode ser substituida por: vazao_cota_qualquer = CURVA_VAZOES[contador]
        #   Calcular SdtQ2[contador]
        SdtQ2[contador] = ((float(2*volume_armazenado*(10**6))/DURACAO_INTERVALO_TEMPO) + vazao_cota_qualquer)
    
############ Removido dia 2016/04/28    
####    #   Loop para montar SdtQ. Ele e' construido para todas as alturas, logo, ele utiliza as alturas compreendidas na curva cota-volume.
####    for altura in xrange(len(cotas_interpoladas)):
####        
####        ### OBSERVACAO ###############################################################################
####        #   E' possivel que o loop abaixo de erro se o primeiro valor da curva de vazoes nao for zero#
####        #   Testes devem ser feito para testar se isto e' verdade.                                   #
####        #   Possivel solucao: trocar < por <=                                                        #
####        ##############################################################################################
####        
####        #   Loop para ver se ha' altura suficiente para que as vazoes participem to calculo
####        if cotas_interpoladas[altura] < min(ALTURAS_VAZOES_CALCULADAS): #isto e', se as vazoes de saida nao participam do calculo ainda.
####            volume_cota_qualquer = interp_cota_volume(cotas_interpoladas[altura])
####            SdtQ[altura] = ( ((2 * volume_cota_qualquer * (10**6))/DURACAO_INTERVALO_TEMPO) ) #   como a cota da agua e' menor que a cota do inicio da curva de extravasao a vazao saida e' nula
####        
####        #   Isto e', se a altura >= COTA_INICIO_EXTRAVASAO
####        else:
####            volume_cota_qualquer    = interp_cota_volume(cotas_interpoladas[altura])
####            vazao_cota_qualquer = interp_cota_vazao(cotas_interpoladas[altura])  #  interpolar a curva de saida de vazao para tirar um valor de vazao para a altura calculada que pode ser diferente das alturas usadas no calculo da curva de vazao
####            SdtQ[altura] = ( ((2 * volume_cota_qualquer * (10**6))/DURACAO_INTERVALO_TEMPO) + vazao_cota_qualquer)
####            
############
        
####    for i in xrange(101): #loop para "preencher" SdtQ
####        armazenamento_qualquer = (interp_cota_volume(cotas_interpoladas[i]) * (10**6))          #interpola LINEARMENTE ENTRE DOIS PONTOS CONSECUTIVOS para saber o armazenamento do reservatorio com cota qualquer.
####        vazao_saida_qualquer   = interp_cota_vazao(cotas_interpoladas[i])                       #interpola LINEARMENTE ENTRE DOIS PONTOS CONSECUTIVOS para saber a vazao de saida do reservatorio com cota qualquer
####                                                                                                #Esta linha nao e' necessaria, ja' que a interpolacao da vazao e' realizada com a altura_calculada, mas serve para lembrar o programador
####        SdtQ[i] = ((2 * armazenamento_qualquer/DURACAO_INTERVALO_TEMPO) + vazao_saida_qualquer) #parcela 2*S/dt + Q
        
########    for i in xrange(101): #loop para "preencher" SdtQ
#        armazenamento_qualquer = (interp_cota_volume(cotas_interpoladas[i]) * (10**6))          #interpola LINEARMENTE ENTRE DOIS PONTOS CONSECUTIVOS para saber o armazenamento do reservatorio com cota qualquer.
#        vazao_saida_qualquer   = interp_cota_vazao(cotas_interpoladas[i])                       #interpola LINEARMENTE ENTRE DOIS PONTOS CONSECUTIVOS para saber a vazao de saida do reservatorio com cota qualquer
#                                                                                                #Esta linha nao e' necessaria, ja' que a interpolacao da vazao e' realizada com a altura_calculada, mas serve para lembrar o programador
########        SdtQ[i] = (((2 * volumes_calculados[i] * (10**6))/DURACAO_INTERVALO_TEMPO) + CURVA_VAZOES[i]) #parcela 2*S/dt + Q
        
                            # Comeca aqui as iteracoes do metodo de Puls #
                            
    interp_sdtq1_alturas = interp1d(SdtQ1, cotasSdtQ1)                 
    interp_sdtq2_alturas = interp1d(SdtQ2, ALTURAS_VAZOES_CALCULADAS)  
    cota_atual          = COTA_INICIAL                                  # A cota do primeiro loop e' a cota inicial do reservatorio
    volume_reservado    = [0 for i in xrange(NUMERO_INTERVALOS_TEMPO)] # Variavel que controla o volume armazenado
    S2dtQ               = [0 for i in xrange(NUMERO_INTERVALOS_TEMPO)] # Variavel usada no puls... 2 * S(t+1)/dt + Q
    HIDROGRAMA_SAIDA    = [0 for i in xrange(NUMERO_INTERVALOS_TEMPO)] # Criar a variavel que armazena os valores do hidrograma de saida - e' retornada por isso esta' toda em maiusculo
    
        #    Como e' o primeiro loop, os valores de volume armazenado e vazao e saida sao em funcao da nivel d'agua, pois nao foi perdido e nem recebido volumes.
        
    ### OBSERVACAO ###############################################################################
    #   E' possivel que o loop abaixo de erro se o primeiro valor da curva de vazoes nao for zero#
    #   Testes devem ser feito para testar se isto e' verdade.                                   #
    #   Possivel solucao: trocar >= por >                                                        #
    ##############################################################################################
        
    #   loop para encontrar a vazao de saida da primeira iteracao do puls: ele e' necessario pois a funcao que interpola os valores na curva de vazao possuem intervalo menor que os valores de alturas calculadas
    if cota_atual >= min(ALTURAS_VAZOES_CALCULADAS): #isto e', se o nivel do reservatorio esta' tao alto que ja' esta extravasando. Ele pode ser igual a min(ALTURAS_VAZOES_CALCULADAS) porque o primeiro valor da curva de vazoes e' sempre zero;
        
        HIDROGRAMA_SAIDA[0] = interp_cota_vazao(cota_atual)  #eu jogo a cota atual na funcao de interpolacao e tiro o valor de vazao interpolado
        volume_reservado[0] = (interp_cota_volume(cota_atual) * (10**6))  # Achar o volume armazenado  - primeiro loop
        
    #   Caso o reservatorio esta' com cota abaixo da cota de inicio de extravasao, a vazao de saida inicial e' zero.
    else:
        
        HIDROGRAMA_SAIDA[0]  = 0.0
        volume_reservado[0] = (interp_cota_volume(cota_atual) * (10**6))  # Achar o volume armazenado  - primeiro loop
        
        
##    print "int., cota do reserv."
##    print "   1, %11.6f" %(cota_atual)
#    volume_armazenado[0] = (interp_cota_volume(cota_atual) * (10**6))  # Achar o volume armazenado  - primeiro loop
    
    
    #### Adicionado para checar a correcao #### INICIO
#    print "Antes do primeiro loop: "
#    print "HIDROGRAMA_SAIDA[0] = " + str(HIDROGRAMA_SAIDA[0])
#    print "volume_armazenado[0] = " + str(volume_armazenado[0])
#    print "Agora comecam os loops do puls: \n"
#    print " numLoop,        S2dtQ,   cota_atual, volum_armaze, hidrog_saida"
##    print " numLoop,         S2dtQ = hid_entra_0 + hid_entra_1 +   2*volume/dt - hid_saida_0"
    #### Adicionado para checar a correcao #### FIM
 
        # Comeca o loop principal do metodo.
    for main_loop in xrange(0, (NUMERO_INTERVALOS_TEMPO-1)): #um a menos, pois usa-se o valor (intervalo+1). Se nao reduzir 1 da index error.
        
            # calculos para determinacao do proximo valor do hidrograma de saida
        S2dtQ[main_loop] = ( HIDROGRAMA_ENTRADA_PULS[main_loop] + HIDROGRAMA_ENTRADA_PULS[(main_loop+1)] + (2*volume_reservado[main_loop]/DURACAO_INTERVALO_TEMPO) - HIDROGRAMA_SAIDA[main_loop] ) # Determinacao do 2*St+dt/dt + Qt+dt para
                                                                                                                                                                        #entrar na tabela do SdtQ e descobrir os valores a serem interpolados.
############ desativado 2016/04/28
####            #mudanca de estrategia: descobrir o nivel de agua correspondete ao S2dtQ calculado ao inves de interpolar a tabela SdtQ
####        try: #tento encontrar a cota atual, caso o nivel de agua extrapole a curva, pare o programa.
####            cota_atual = interp_sdtq_alturas(S2dtQ[main_loop]) #obter o nivel de agua correspondente ao S2dtQ calculado (que normalmente e' comparado com o SdtQ para saber quais posicoes interpolar)
####            
####        except: #caso o S2dtQ ter um valor muito grande, ele vai cair fora da curva, neste caso, dizer que o puls 'falhou', pois o programa nao extrapola a curva cota-volume.
####            showinfo("Erro: Reservatorio subestimado", "Não foi possível finalizar o cálculo de uma operação de Puls.\nMotivo: O nível do reservatório alcançou uma cota que não está compreendida entre as cotas fornecidas pelo usuário (o modelo não extrapola a curva cota-volume).") #"Voce e' burro." ahahhahahaha
####            showinfo("Sugestões", "1 - Forneça mais dados para a curva cota-volume.\n2 - Modifique as estruturas de saída de vazão existentes.\n3 - Aumente o número de estruturas de saída de vazão.\n\nO modelo será finalizado, tente novamente.") #"Voce e' burro." ahahhahahaha
####            sys.exit()
############
        
        #   Se o valor de S2dtQ calculado neste loop esta' entre os valores de SdtQ1
        if (( S2dtQ[main_loop] >= min(SdtQ1) ) and ( S2dtQ[main_loop] < max(SdtQ1) )):
            #   Tirar a nova cota...
            cota_atual = interp_sdtq1_alturas(S2dtQ[main_loop])
            
        #   Se os valorde S2dtQ calculado neste loop esta' entre os valores de SdtQ2
        elif (( S2dtQ[main_loop] >= min(SdtQ2) ) and ( S2dtQ[main_loop] <= max(SdtQ2) )):
            #   Tirar a nova cota...
            cota_atual = interp_sdtq2_alturas(S2dtQ[main_loop])
        
        #   Caso nao esta' compreendido em nenhum dos intervalos, o reservatorio esta subdimensionado
        else:
            showinfo("Erro: Reservatorio subestimado", "Não foi possível finalizar o cálculo de uma operação de Puls.\nMotivo: O nível do reservatório alcançou uma cota que não está compreendida entre as cotas fornecidas pelo usuário (o modelo não extrapola a curva cota-volume).") #"Voce e' burro." ahahhahahaha
            showinfo("Sugestões", "1 - Forneça mais dados para a curva cota-volume.\n2 - Modifique as estruturas de saída de vazão existentes.\n3 - Aumente o número de estruturas de saída de vazão.\n\nO modelo será finalizado, tente novamente.") #"Voce e' burro." ahahhahahaha
            sys.exit()
            
        ### OBSERVACAO ###############################################################################
        #   E' possivel que o loop abaixo de erro se o primeiro valor da curva de vazoes nao for zero#
        #   Testes devem ser feito para testar se isto e' verdade.                                   #
        #   Possivel solucao: trocar >= por >                                                        #
        ##############################################################################################
        
        #   loop para encontrar a vazao de saida da primeira iteracao do puls: ele e' necessario pois a funcao que interpola os valores na curva de vazao possuem intervalo menor que os valores de alturas calculadas
        if cota_atual >= min(ALTURAS_VAZOES_CALCULADAS): #isto e', se o nivel do reservatorio esta' tao alto que ja' esta extravasando. Ele pode ser igual a COTA_INICIO_EXTRAVASAO porque o primeiro valor da curva de vazoes e' sempre zero;

            #    usar o nivel de agua encontrado para seguir para determinacao do armazenado e a vazao de saida.  ##### ESTAS LINHAS PODEM DAR ERRO -> VALOR DE cota_atual CAIR FORA DO INTERVALO DE INTERPOLACAO.....
            volume_reservado[(main_loop+1)] = (interp_cota_volume(cota_atual) * (10**6))  # S(t+dt) = ..... interpolacao
            HIDROGRAMA_SAIDA[(main_loop+1)]  = interp_cota_vazao(cota_atual)               # Q(t+dt) = ..... interpolacao
            
        #   Ou seja, a cota atual do reservatorio continua abaixo da cota que comeca a sair vazao
        else:

            #    usar o nivel de agua encontrado para seguir para determinacao do armazenado e a vazao de saida.  ##### ESTAS LINHAS PODEM DAR ERRO -> VALOR DE cota_atual CAIR FORA DO INTERVALO DE INTERPOLACAO.....
            volume_reservado[(main_loop+1)] = (interp_cota_volume(cota_atual) * (10**6))  # S(t+dt) = ..... interpolacao
            HIDROGRAMA_SAIDA[(main_loop+1)]  = 0                                           # Cota insuficiente, nao gera saida de vazao
    
##        print "%4d, %11.6f" %((main_loop+2), cota_atual)
        #### Adicionado para checar a correcao #### INICIO
#        print " %7d, %11.6f, %11.6f, %11.6f, %11.6f" %(main_loop, S2dtQ[main_loop], cota_atual, volume_armazenado[(main_loop+1)], HIDROGRAMA_SAIDA[(main_loop+1)])
##        print " %7d, %11.6f = %11.6f + %11.6f + %11.6f + %11.6f" %(main_loop, S2dtQ[main_loop], HIDROGRAMA_ENTRADA_PULS[main_loop], HIDROGRAMA_ENTRADA_PULS[(main_loop+1)], (2*volume_armazenado[main_loop]/DURACAO_INTERVALO_TEMPO), HIDROGRAMA_SAIDA[main_loop] )
        #### Adicionado para checar a correcao #### FIM
    
    return HIDROGRAMA_SAIDA
    
#_______________________________________________________________________#   

def plotar_Hidrogramas_PULS(HIDROGRAMA_ENTRA, HIDROGRAMA_SAI, NUMERO_INTERVALOS_TEMPO, caminho_saida, nome_posto, numero_do_grafico):
    """
    Funcao que plota os hidrogramas de entrada e saida de uma operacao Puls qualquer, salvando-os em uma imagem .png no diretorio fornecido.
    
    Nenhuma variavel e' retornada pela funcao.
    
    Parametros para uso:
        
            HIDROGRAMA_ENTRA: Lista que contem os dados do hidrograma de entrada do reservatorio.
                -> Esta variavel deve ser estruturada da seguinte forma:
                HIDROGRAMA_ENTRA = [...] -> Dados de entrada de vazao [em metros^3/s].
                
            HIDROGRAMA_SAI: Lista que contem os dados do hidrograma de saida do reservatorio.
                -> Esta variavel deve ser estruturada da seguinte forma:
                HIDROGRAMA_SAI = [...] -> Dados de saida de vazao [em metros^3/s].
            
            NUMERO_INTERVALOS_TEMPO: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            
            caminho_saida: Variavel do tipo string que armazena o diretorio em que a imagem sera' salva.
            
            nome_posto: Variavel do tipo string que armazena o titulo do grafico.
            
            numero_do_grafico: Variavel do tipo inteira que serve para diferenciar cada plotagem (evita que ocorra substituicao de arquivos).
                -> OBS: Esta variavel deve assumir um valor diferente para cada plotagem. 
                        E' recomendado utilizar o numero da operacao como valor para numero_do_grafico.
                        O nome final do arquivo e': (caminho_saida)/PlotagensPULS/Operacao_(numero_do_grafico)_Puls.png
            
    """
    
    import matplotlib.pyplot as plt
    from numpy import linspace
    import os
    
    
        #Agora que eu deletei a pasta antiga, faca uma nova para salvar os graficos 
    if not os.path.exists(caminho_saida + "/PlotagensPULS"):
        os.makedirs(caminho_saida + "/PlotagensPULS")
    
        #****---- PLOTAGEM ----****#
    
    fig = plt.figure(figsize=(15,9), dpi=60)
    ax5 = fig.add_axes([0.126, 0.1, 0.772, 0.8]) #ajustar a tela
    
    altura_maxima_grafico = (4./3. * (max(HIDROGRAMA_ENTRA))) #ajustar a "escala" vertical do grafico
    
    l1 = ax5.plot(HIDROGRAMA_ENTRA, 'b-', linewidth=4, label = 'HID. ENTRADA')  #plotagem
    l2 = ax5.plot(HIDROGRAMA_SAI, 'r-', linewidth=4, label = 'HID. SAIDA') #plotagem
    
    ax5.set_xlabel('Intervalos de tempo', size = 15)   #nome do eixo x
    ax5.set_ylabel('Vazao (m3/s)', color='b', size = 15)       #nome e cor do nome do eixo y         
    for corlabel1 in ax5.get_yticklabels():         #trocar a cor dos valores do eixo y
        corlabel1.set_color('b')
        
    grid_horizontal_1 = linspace((0),(altura_maxima_grafico),(5)) #grid horizontal (eixo y)
    grid_vertical = linspace((0),(NUMERO_INTERVALOS_TEMPO-1),(5)) #grid vertical (eixo y)
    
    ax5.xaxis.set_ticks(grid_vertical) #nomear grid
    ax5.yaxis.set_ticks(grid_horizontal_1) #nomear grid
    ax5.grid(True) #Ligar/Desligar o grid
    
     #Anotacoes
    plt.annotate('dQ = %0.2f m3/s' %(max(HIDROGRAMA_ENTRA) - max(HIDROGRAMA_SAI)), xy = ((0.75*(len(HIDROGRAMA_ENTRA))),(max(HIDROGRAMA_ENTRA)*0.9)),  xycoords='data', xytext=None, color = 'b' ,textcoords=None)#"Tabelinha"   

    plt.legend(loc='upper right')
    
    plt.title((str(nome_posto) + '\nPuls'), size = 15) 
    
    plt.savefig(str(caminho_saida) + '/PlotagensPULS/Operacao_' + str(numero_do_grafico) + '_Puls.png')  #salvar imagem do grafico
    
    fig.clf('all') #nao armazenar os graficos na memoria
    plt.close('all') #fechar as figuras pra nao armazenar na memoria

#_______________________________________________________________________# 
 #    PROPAGACAO EM RIOS utilizando-se do MODELO DE MUSKINGUN-CUNGE    #
#Baseou-se no Livro Modelos Hidrologicos de Carlos E. M. Tucci e no livro Python Hydrology de Sat Kumar Tomer.

def aplicar_MuskingunCunge(HIDROGRAMA_ENTRADA, NUMERO_INTERVALOS_TEMPO, DURACAO_INTERVALO_TEMPO, DIFERENCA_COTA, COMPRIMENTO_CANAL, LARGURA_CANAL, COEF_RUGOSIDADE):
    """
    
    """
    from tkMessageBox import showinfo
    import sys
    from math import ceil
    
    
        #achar a posicao do pico do hidrograma (tempo de subida do hidrograma)
    posicao_pico = HIDROGRAMA_ENTRADA.index(max(HIDROGRAMA_ENTRADA))
    
        #determinar o deltaT (EM SEGUNDOS!!!) ->>>> deltaT = tempo_pico/5.
    delta_t = (posicao_pico * DURACAO_INTERVALO_TEMPO)/5.
    
        #determinar a vazao de referencia -> vazao_referencia = vazao_pico * 2/3. ->>>>>>>>>> 
    vazao_referencia = max(HIDROGRAMA_ENTRADA)*2/3.
    
        #calcular a declividade (m/m)
    declividade = (DIFERENCA_COTA/(COMPRIMENTO_CANAL*1000))
    
        #calcular a celeridade (m/s)
    celeridade = (  ( 5/3. * ((declividade)**0.3) * ((vazao_referencia)**0.4) )/( ((COEF_RUGOSIDADE)**0.6) * ((LARGURA_CANAL)**0.4) )  )
    
        #calcular o delta X, para entao descobrir em quantos trechos o canal sera' dividido.
    delta_x = (  (celeridade*delta_t*0.5) * (1 + ( 1 + ((1.5 * vazao_referencia)/(LARGURA_CANAL * declividade * delta_t * ((celeridade)**2))) )**0.5)  )
    
        #Algoritmo para decidir em quantos trechos o canal sera' dividido
    numero_trechos = int(ceil((COMPRIMENTO_CANAL*1000)/delta_x))
    
        #calcular novo delta X
    delta_x = ((COMPRIMENTO_CANAL*1000)/numero_trechos)
    
        #calcular coeficientes K (segundos) e X 
    coef_K = (delta_x/celeridade)  
    coef_X = ( 0.5 * (1 - ( (vazao_referencia)/(LARGURA_CANAL * declividade * celeridade * delta_x) )) )
    
        #verificacao das condicoes -> caso nao satisfaz, parar o modelo.
#    if ( ((delta_t/coef_K) < (2 * coef_X)) or ((delta_t/coef_K) > (2 * (1-coef_X))) ):
    if ( ((delta_t/coef_K) < (2 * coef_X)) ):
            
            #Caixa de dialogo
        showinfo("Erro: Operação hidrológica inválida", "As condições de validade da operação de Muskingun-Cunge não são atendidas.\nO modelo será finalizado. Tente novamente.") #"Voce e' burro." ahahhahahaha
        showinfo("Erro: Operação hidrológica inválida", "A condição delta_t/K < 2*X não é satisfeita.") #"Voce e' burro." ahahhahahaha
        sys.exit() #corrigir esta linha.... ela faz o modelo dar pau por nao fechar ele corretamente....
        
        #verificacao das condicoes -> caso nao satisfaz, parar o modelo.
    if ( ((delta_t/coef_K) > (2 * (1-coef_X))) ):
            
            #Caixa de dialogo
        showinfo("Erro: Operação hidrológica inválida", "As condições de validade da operação de Muskingun-Cunge não são atendidas.\nO modelo será finalizado. Tente novamente.") #"Voce e' burro." ahahhahahaha
        showinfo("Erro: Operação hidrológica inválida", "A condição delta_t/K > 2*(1-X) não é satisfeita.") #"Voce e' burro." ahahhahahaha
        sys.exit() #corrigir esta linha.... ela faz o modelo dar pau por nao fechar ele corretamente....
    
    else: #ou seja, ambas as condicoes de validade sao verificadas.
        
            #calcular C1, C2 e C3:
        coef_c1 = ( (delta_t - (2 * coef_K * coef_X))/(delta_t + (2 * coef_K * (1 - coef_X))) )
        coef_c2 = ( (delta_t + (2 * coef_K * coef_X))/(delta_t + (2 * coef_K * (1 - coef_X))) )
        coef_c3 = ( ((delta_t * (-1)) + (2 * coef_K * (1 - coef_X)))/(delta_t + (2 * coef_K * (1 - coef_X))) )
        
            #Declarar variavel de saida - > saida do canal e' o ultimo hidrograma desta variavel.
        hidrogramas_trechos = [[0. for i in xrange(NUMERO_INTERVALOS_TEMPO)] for i2 in xrange(numero_trechos)] #armazena os hidrogramas de cada trecho do canal...
        
            #loop da propagacao do canal
        for trecho in xrange(numero_trechos): #calcular trecho a trecho....a saida e' o resultado do ultimo trecho (y).
            
                #se for primeiro loop e' diferente....
            if trecho == 0: #se for o primeiro trecho, o algoritmo e' um pouco diferente

                    #primeiro valor e' sempre igual...
                hidrogramas_trechos[trecho][0] = HIDROGRAMA_ENTRADA[0] #o primeiro valor do hidrograma de saida e' igual ao primeiro valor do hidrograma de entrada
                
                    #loop dos demais intervalos de tempo...
                for intervalo in xrange(1, NUMERO_INTERVALOS_TEMPO): # comeca em 1 pois o zero ja' foi feito anteriormente
                    
                        #calcular demais valores...
                    hidrogramas_trechos[trecho][intervalo] = ((coef_c1 * HIDROGRAMA_ENTRADA[intervalo]) + (coef_c2 * HIDROGRAMA_ENTRADA[(intervalo-1)]) + (coef_c3 * hidrogramas_trechos[trecho][(intervalo - 1)]))
            
                #demais loops....
            else: #ou seja, se nao for mais o primeiro trecho....(trecho = 1,2,3,4,5.....)
                
                    #primeiro valor e' sempre igual...
                hidrogramas_trechos[trecho][0] = hidrogramas_trechos[(trecho - 1)][0] #o primeiro valor do hidrograma de saida e' igual ao primeiro valor do hidrograma do trecho anterior
                
                    #loop dos demais intervalos de tempo...
                for intervalo in xrange(1, NUMERO_INTERVALOS_TEMPO): # comeca em 1 pois o zero ja' foi feito anteriormente
                    
                        #calcular demais valores...
                    hidrogramas_trechos[trecho][intervalo] = ((coef_c1 * hidrogramas_trechos[(trecho - 1)][intervalo]) + (coef_c2 * hidrogramas_trechos[(trecho - 1)][(intervalo - 1)]) + (coef_c3 * hidrogramas_trechos[trecho][(intervalo - 1)]))
                
    return hidrogramas_trechos[-1] #retorna o hidrograma do ultimo trecho.
    
#_______________________________________________________________________# 

def plotar_Hidrogramas_MKC(HIDROGRAMA_ENTRA, HIDROGRAMA_SAI, NUMERO_INTERVALOS_TEMPO, caminho_saida, nome_posto, numero_do_grafico):
    """
    
    """
    import matplotlib.pyplot as plt
    from numpy import linspace
    import os
    
    
        #Agora que eu deletei a pasta antiga, faca uma nova para salvar os graficos 
    if not os.path.exists(caminho_saida + "/PlotagensMKC"):
        os.makedirs(caminho_saida + "/PlotagensMKC")
    
        #****---- PLOTAGEM ----****#
    
    fig = plt.figure(figsize=(15,9), dpi=60)
    ax5 = fig.add_axes([0.126, 0.1, 0.772, 0.8]) #ajustar a tela
    
    altura_maxima_grafico = (4./3. * (max(HIDROGRAMA_ENTRA))) #ajustar a "escala" vertical do grafico
    
    l1 = ax5.plot(HIDROGRAMA_ENTRA, 'b-', linewidth=4, label = 'HID. ENTRADA')  #plotagem
    l2 = ax5.plot(HIDROGRAMA_SAI, 'r-', linewidth=4, label = 'HID. SAIDA') #plotagem
    
    ax5.set_xlabel('Intervalos de tempo', size = 15)   #nome do eixo x
    ax5.set_ylabel('Vazao (m3/s)', color='b', size = 15)       #nome e cor do nome do eixo y         
    for corlabel1 in ax5.get_yticklabels():         #trocar a cor dos valores do eixo y
        corlabel1.set_color('b')
        
    grid_horizontal_1 = linspace((0),(altura_maxima_grafico),(5)) #grid horizontal (eixo y)
    grid_vertical = linspace((0),(NUMERO_INTERVALOS_TEMPO-1),(5)) #grid vertical (eixo y)
    
    ax5.xaxis.set_ticks(grid_vertical) #nomear grid
    ax5.yaxis.set_ticks(grid_horizontal_1) #nomear grid
    ax5.grid(True) #Ligar/Desligar o grid
    
#     #Anotacoes
#    plt.annotate('dQ = %0.2f m3/s' %(max(HIDROGRAMA_ENTRA) - max(HIDROGRAMA_SAI)), xy = ((0.75*(len(HIDROGRAMA_ENTRA))),(max(HIDROGRAMA_ENTRA)*0.9)),  xycoords='data', xytext=None, color = 'b' ,textcoords=None)#"Tabelinha"   

    plt.legend(loc='upper right')
    
    plt.title((str(nome_posto) + '\nMuskingun-Cunge'), size = 15) 
    
    plt.savefig(str(caminho_saida) + '/PlotagensMKC/Operacao_' + str(numero_do_grafico) + '_Muskingun-Cunge.png')  #salvar imagem do grafico
    
    fig.clf('all') #nao armazenar os graficos na memoria
    plt.close('all') #fechar as figuras pra nao armazenar na memoria

#_______________________________________________________________________#

def somar_Hidrogramas(NUMERO_INTERVALOS_TEMPO, hidrogramas):
    """
    Esta funcao soma N hidrogramas resultando em um unico so'. 
    
    Ressalta-se que a funcao considera que todos os hidrogramas acontecessem ao mesmo tempo, isto e', o valor de cada intervalo do
hidrograma resultante e' a soma dos valores deste mesmo intervalo de tempo de todos os N hidrogramas. Segue um exemplo uma soma de dois hidrogramas:

    Hidrog. Resultante =  Hidrog.1 + Hidrog.2
           5           =    2      +    3
          10           =    6      +    4
          16           =    9      +    7
         ...           =   ...     +   ... 
         
    Parametros para uso:
        
            NUMERO_INTERVALOS_TEMPO: Variavel do tipo inteiro que armazena o numero de intervalos de tempo da operacao.
            
            hidrogramas: Variavel do tipo lista que armazana os hidrogramas que serao somados.
                -> Esta variavel deve ser estruturada da seguinte forma:
                hidrogramas = [[...],[...],[...],[...], ... ] -> Em que cada [...] e' um hidrograma que participara' da soma;
                                                              -> Cada hidrograma ( [...] ) deve ter o mesmo numero de dados (tamanho).
                                                              -> Nao ha' restricao do numero de hidrogramas a serem somados.
                     
    """
    
    #Algoritmo original escrito por Vitor G. Geller
    
    from tkMessageBox import showinfo
    import sys
        
        
        #variavel que armazenara' o somatorio
    hidrograma_resultante = [0. for i in xrange(NUMERO_INTERVALOS_TEMPO)]
    
            #--- Os hidrogramas a serem somados entram como listas dentro da lista hidrogramas.
            #--- hidrogramas = [[hid_1],[hid_2],[hid_3],...,[hid_n]]
            
        #fazer uma rapida checagem no tamanho dos hidrogramas de entrada
    for hidrograma in xrange(len(hidrogramas)):
        
        if (len(hidrogramas[hidrograma]) != NUMERO_INTERVALOS_TEMPO):
            showinfo("Erro.", "O número de elementos do hidrograma %i é diferente do número de intervalos de tempo.\nO modelo será finalizado. Revise os hidrogramas de entrada." %(hidrograma+1)) #"Voce e' burro." ahahhahahaha
            sys.exit()
    
    else: #todos possuem o mesmo tamanho, e' so' somar tudo.
        
            #loop dos intervalos
        for nint_tempo in xrange(NUMERO_INTERVALOS_TEMPO):
            
                #declarar/resetar a variavel que recebe a soma dos hidrogramas no intervalo de tempo qualquer
            somatorio_do_intervalo = 0
            
                #loops dos hidrogramas
            for i2 in xrange(len(hidrogramas)):
                
                    #somar/acumular N parcelas de um mesmo intervalo de tempo
                somatorio_do_intervalo += hidrogramas[i2][nint_tempo]
                
                #armazenar a soma no intervalo correspondente
            hidrograma_resultante[nint_tempo] = somatorio_do_intervalo
            
            # hidrograma resultante e' a simples soma pontual (mesmo intervalo de tempo) dos hidrogramas anteriores.
        return hidrograma_resultante
#_______________________________________________________________________#
#
def plotar_somar_Hidrogramas(HIDROGRAMA_SAI, valores_hidrogramas_da_juncao, nint_tempo, caminho_saida, nome_posto, numero_do_grafico ):
    """
    Funcao responsavel por plotar e salvar os hidrogramas calculados nas operacoes juncao. 
    """
    
    #Algoritmo original escrito por Vitor Geller.
    
    import matplotlib.pyplot as plt
    import os
    from numpy import array, linspace    
    
        
        #Agora que eu deletei a pasta antiga, faca uma nova para salvar os graficos 
    if not os.path.exists(caminho_saida + "/PlotagensJUNCAO"):
        os.makedirs(caminho_saida + "/PlotagensJUNCAO")
        
              
    altura_maxima_grafico = (4/3. * (max(HIDROGRAMA_SAI))) #ajustar a "escala" vertical do grafico
        
    x = array([i for i in xrange( nint_tempo )])  #transforma eixo x em array (primeira plotagem)
                    
    fig = plt.figure(figsize=(15,9), dpi=60)    #inicio da primeira plotagem
    ax1 = fig.add_axes([0.126, 0.1, 0.772, 0.8]) #ajustar a tela
    
    plt.axis([0, nint_tempo, 0, (altura_maxima_grafico)])  #declarar eixos
    ax1.plot(x, HIDROGRAMA_SAI, linewidth=4, label = 'Vazao de resultante')  #plotagem
    
    for i in xrange( len(valores_hidrogramas_da_juncao) ):
        ax1.plot(x, valores_hidrogramas_da_juncao[i], linewidth=4, label = ('Hidrograma ' + str(i+1)))  #plotagem
        
    ax1.set_xlabel('Intervalos de tempo', size = 15)   #nome do eixo x
    ax1.set_ylabel('Vazao (m3/s)', color='b', size = 15)       #nome e cor do nome do eixo y         

    for corlabel1 in ax1.get_yticklabels():         #trocar a cor dos valores do eixo y
        corlabel1.set_color('b')
            
    grid_horizontal_1 = linspace((0),(altura_maxima_grafico),(5)) #grid horizontal (eixo y)
    grid_vertical = linspace((0),(nint_tempo),(5)) #grid vertical (eixo y)
    
    ax1.xaxis.set_ticks(grid_vertical) #nomear grid
    ax1.yaxis.set_ticks(grid_horizontal_1) #nomear grid
    ax1.grid(True) #Ligar/Desligar o grid
            
    plt.title((str(nome_posto) + '\nJuncao'), size = 15)
    
    plt.legend(loc='upper right')
                  
    plt.savefig(str(caminho_saida) + "/PlotagensJUNCAO/Operacao_" + str(numero_do_grafico) + '_Juncao.png')  #salvar imagem do grafico
    
    fig.clf('all') #nao armazenar os graficos na memoria
    plt.close('all') #fechar as figuras pra nao armazenar na memoria

#_______________________________________________________________________#  

def aplicar_MetodoSilveira():
    """
    Estima a ... a partir do metodo Silveira.
    
        Parametros para uso:
            
            
    """
    
    print "metodo silveira"
    
#_______________________________________________________________________#

def aplicar_PenmanMonteith():
    """
    Determina a evapotranspiracao a partir do metodo Penman-Monteith.
    
        Parametros para uso:
            
            
    """
    
    print "Penman-Monteith"