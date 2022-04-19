from distutils.log import info
import linecache
from random import randint, choice, random
from statistics import quantiles
from threading import local

from soupsieve import select
from mochila import mochila
from state import State
from time import sleep
import math
import os
#import numpy as np

class SocorrePlan:
    def __init__(self, maxRows, maxColumns, goal, initialState, name = "none", mesh = "square"):
        """
        Define as variaveis necessárias para a utilização do random plan por um unico agente.
        """
        self.walls = []
        self.maxRows = maxRows
        self.maxColumns = maxColumns
        self.initialState = initialState
        self.currentState = initialState
        self.goalPos = goal
        self.actions = []
        
        ##ALTERACOES
        self.acaoPadrao = 0 ##index da lista de possiveis direcoes
        self.vitimasSalvas = 0
        self.voltaParaBase = False
        self.infoVitimas = []
        self.mapa = {}
        self.linhaAtual = self.initialState.row
        self.colunaAtual = self.initialState.col

        self.possibilities = ["N", "S", "L", "O", "NE", "NO", "SE", "SO"]
        self.movePos = { "N" : (-1, 0),
                    "S" : (1, 0),
                    "L" : (0, 1),
                    "O" : (0, -1),
                    "NE" : (-1, 1),
                    "NO" : (-1, -1),
                    "SE" : (1, 1),
                    "SO" : (1, -1)}
 

    def setWalls(self, walls):
        row = 0
        col = 0
        for i in walls:
            col = 0
            for j in i:
                if j == 1:
                    self.walls.append((row, col))
                col += 1
            row += 1
       
        
    def updateCurrentState(self, state):
         self.currentState = state

    def isPossibleToMove(self, toState):
        """Verifica se eh possivel ir da posicao atual para o estado (lin, col) considerando 
        a posicao das paredes do labirinto e movimentos na diagonal
        @param toState: instancia da classe State - um par (lin, col) - que aqui indica a posicao futura 
        @return: True quando é possivel ir do estado atual para o estado futuro """

        ## vai para fora do labirinto
        if (toState.col < 0 or toState.row < 0):
            return False

        if (toState.col >= self.maxColumns or toState.row >= self.maxRows):
            return False
        
        if len(self.walls) == 0:
            return True
        
        ## vai para cima de uma parede
        if (toState.row, toState.col) in self.walls:
            return False

        # vai na diagonal? Caso sim, nao pode ter paredes acima & dir. ou acima & esq. ou abaixo & dir. ou abaixo & esq.
        delta_row = toState.row - self.currentState.row
        delta_col = toState.col - self.currentState.col

        ## o movimento eh na diagonal
        if (delta_row !=0 and delta_col != 0):
            if (self.currentState.row + delta_row, self.currentState.col) in self.walls and (self.currentState.row, self.currentState.col + delta_col) in self.walls:
                return False
        
        return True

    """def acaoContraria(self, movPos, acao):

        acaoContraria = movPos[acao]
        x = acaoContraria[0] * -1
        y = acaoContraria[1] * -1
        acaoContraria = (x, y)
        
        for key, value in movPos.items():
         if acaoContraria == value:
             acaoContraria = key

        return acaoContraria

    def distanciaEuclidiana(self, pos1, pos2):
        x1 = pos1[0]
        x2 = pos2[0]
        y1 = pos1[1]
        y2 = pos2[1]
        
        deltaX = x1-x2
        deltaY = y1-y2

        quadradoX = math.pow(deltaX, 2)
        quadradoY = math.pow(deltaY, 2)

        somaQuadrados = quadradoX + quadradoY

        euclidiana = math.sqrt(somaQuadrados)

        return euclidiana

    def encontra_estado_mais_promissor (self, franja, heuristica_estados):
        valor_mais_promissor = 1000000000
        ##estado_mais_promissor = None
        indice_mais_promissor = 0
        indice = 0
        for estado in franja:
            if heuristica_estados[estado] < valor_mais_promissor:
                ##estado_mais_promissor = estado
                valor_mais_promissor = heuristica_estados[estado]
                indice_mais_promissor = indice
            indice = indice + 1
        return indice_mais_promissor


    def encontra_estados_sucessores (self, dicionario, M, N, posicao_atual):
        i = posicao_atual[0]
        j = posicao_atual[1]
        estados_sucessores = []
        if i > 0 and dicionario[i-1, j]["type"]!="parede": # Move para cima na matriz.
            estados_sucessores.append ((i-1, j))
        if i+1 < M and dicionario[i+1, j]["type"]!="parede": # Move para baixo na matriz.
            estados_sucessores.append ((i+1, j))
        if j > 0 and dicionario[i, j-1]["type"]!="parede": # Move para esquerda na matriz.
            estados_sucessores.append ((i, j-1))
        if j+1 < N and dicionario[i, j+1]["type"]!="parede": # Move para direita na matriz.
            estados_sucessores.append ((i, j+1))
        if j > 0 and i > 0 and dicionario[i-1, j-1]["type"]!="parede": # Move diagonalmente para esq sup.
            estados_sucessores.append ((i-1, j-1))
        if j > 0 and i+1 < M and dicionario[i+1, j-1]["type"]!="parede": # Move diagonalmente para esq inf.
            estados_sucessores.append ((i+1, j-1))
        if j+1 < N and i > 0 and dicionario[i-1, j+1]["type"]!="parede": # Move diagonalmente para dir sup.
            estados_sucessores.append ((i-1, j+1))
        if j+1 < N and i+1 < M and dicionario[i+1, j+1]["type"]!="parede": # Move diagonalmente para dir inf.
            estados_sucessores.append ((i+1, j+1))
        return estados_sucessores

    def mostraSolucao (self, estado, predecessores):
        caminho = []
        caminho.append(estado)

        while predecessores[estado] != None:
            caminho.append(predecessores[estado])
            estado = predecessores[estado]
        caminho = caminho[::-1]

        return caminho

    def busca_a_estrela (self, dicionario, M, N, estado_inicial, estado_final):
        distancia_meta = {}
        distancia_percorrida = {}
        heuristica = {}
        predecessores = {}
        estados_expandidos = []
        solucao_encontrada = False

        # Inicializacao de distancia percorrida (f), distancia ate a meta (g) e heuristica (h = f+g).
        distancia_percorrida[estado_inicial] = 0
        distancia_meta[estado_inicial] = self.distanciaEuclidiana(estado_inicial, estado_final) 
        heuristica[estado_inicial] = distancia_percorrida[estado_inicial] + distancia_meta[estado_inicial]
        predecessores[estado_inicial] = None

        franja = [] #franja = fronteira
        franja.append(estado_inicial)
        aux = 1

        #enquanto o tamanho da franja nao for 0
        while len(franja) != 0:
            indice_mais_promissor = self.encontra_estado_mais_promissor(franja, heuristica)
            estado = franja.pop(indice_mais_promissor)
            
            if estado == estado_final:
                solucao_encontrada = True
                break
            
            estados_sucessores = self.encontra_estados_sucessores(dicionario, M, N, estado)
            estados_expandidos.append(estado)
            
            for i in range (0, len(estados_sucessores)):	
                sucessor = estados_sucessores[i]
                if sucessor not in estados_expandidos and sucessor not in franja:
                    franja.append(sucessor)
                    if sucessor not in heuristica.keys():
                        distancia_meta[sucessor] = self.distanciaEuclidiana(sucessor, estado_final)
                        distancia_percorrida[sucessor] = distancia_percorrida[estado] + 1
                        heuristica[sucessor] = distancia_meta[sucessor] + distancia_percorrida[sucessor]
                        predecessores[sucessor] = estado
            aux += 1

        if solucao_encontrada == True:
            caminho = self.mostraSolucao(estado, predecessores)
            return caminho"""
       

    def chooseAction(self, agent):
        """ Escolhe o proximo movimento de forma aleatoria. 
        Eh a acao que vai ser executada pelo agente. 
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """
        ##inicializando o resultado
        result = None

        movePos = { "N" : (-1, 0),
                    "S" : (1, 0),
                    "L" : (0, 1),
                    "O" : (0, -1),
                    "NE" : (-1, 1),
                    "NO" : (-1, -1),
                    "SE" : (1, 1),
                    "SO" : (1, -1)}

        ##se ja salvou tudo
        if len(self.infoVitimas) == 0:
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "resgatouTudo")

        ##se o tempo esta quase na metade -> comecar a voltar
        elif(agent.tempoLivre <= agent.tempoTotal/2 + 2):
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "tempo")
        
        ##se os pacotes acabaram
        elif(agent.pacotes == 0):
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "pacotes")

        ##caso ja tenha recarregado a bateria
        if(result == "recarregou"):
            self.voltaParaBase = False

        elif(result == -1):
            return -1    
        ##se a bateria esta quase na metade -> comecar a voltar
        """elif(agent.bateria <= agent.custoAtual/2 + 2):
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "bateria")"""

        

        ##escolher a acao para voltar para a base, usando o A*
        if(self.voltaParaBase == False):
            estadoInicial = self.currentState.row, self.currentState.col
            
            ##pegando a posicao da vitima para salvar
            vitima = self.infoVitimas[0]
            posicao = (vitima["localizacao"].row, vitima["localizacao"].col)
    
            ##caminho do estado atual ao estado da proxima vitima a ser resgatada
            self.caminho = self.busca_a_estrela(self.mapa, self.maxRows, self.maxColumns, estadoInicial, posicao)
            self.posicaoVetor=1
        
            novaLinha = self.caminho[self.posicaoVetor][0]
            novaColuna = self.caminho[self.posicaoVetor][1]
            i = novaLinha - self.currentState.row
            j = novaColuna - self.currentState.col
            self.posicaoVetor += 1

            posicoes = {(-1, 0) : "N",
                    (1, 0) : "S",
                    (0, 1) : "L",
                    (0, -1) : "O",
                    (-1, 1) : "NE",
                    (-1, -1) : "NO",
                    (1, 1) : "SE",
                    (1, -1) : "SO"}

            movDirection = posicoes[(i, j)]
            state = State(self.currentState.row + movePos[movDirection][0], self.currentState.col + movePos[movDirection][1]) 
            result = [movDirection, state]

            ##diminui a bateria ao tomar a acao
            """if(movDirection in ['N', 'S', 'O', 'L']):
                agent.bateria -= 1 + 0.5 * agent.pacotes

            elif (movDirection in ['NE', 'SE', 'SO', 'NO']):
                agent.bateria -= 1.5 + 0.5 * agent.pacotes"""

            self.funcUnbacktrack(result[0], result[1])

        return result


    def mochilaDinamica(self, quantItens, pesos, valores, capacidade):
        
        mochila = [[0 for i in range(capacidade+1)] for j in range(quantItens+1)]

        for n in range(quantItens+1):
            for cap in range(capacidade+1):
                if n == 0 or cap == 0:
                    mochila[n][cap] = 0
                elif pesos[n-1] <= cap:         
                    mochila[n][cap] = max(valores[n - 1] + mochila[n - 1][cap - pesos[n - 1]], mochila[n - 1][cap])
                else:
                    mochila[n][cap] = mochila[n - 1][cap]

        for i in range(0, quantItens+1):
            for j in range(0, capacidade+1):
                print(mochila[i][j], " ", end='')
            print()

        res = mochila[quantItens][capacidade]
        w = capacidade
        for i in range(quantItens, 0, -1):
            if res <= 0:
                break

            if res == mochila[i - 1][w]:
                continue
            else:
                # This item is included.
                print("Valor", valores[i - 1])
                print("Peso=", pesos[i-1])
             
                # Since this weight is included
                # its value is deducted
                res = res - valores[i - 1]
                w = w - pesos[i - 1]

        return mochila[quantItens][capacidade]

    def printknapSack(self, W, wt, val, n):
        K = [[0 for w in range(W + 1)]
                for i in range(n + 1)]
                
        # Build table K[][] in bottom
        # up manner
        for i in range(n + 1):
            for w in range(W + 1):
                if i == 0 or w == 0:
                    K[i][w] = 0
                elif wt[i - 1] <= w:
                    K[i][w] = max(val[i - 1]
                    + K[i - 1][w - wt[i - 1]],
                                K[i - 1][w])
                else:
                    K[i][w] = K[i - 1][w]
    
        # stores the result of Knapsack
        res = K[n][W]
        print(res)
        """
        w = W

        resgatados= []

        for i in range(n, 0, -1):
            print("i=", i,"w=", w, "res=", res)
            print("k[{}][{}]={}".format(i-1, w, K[i - 1][w])) 
            
            if res <= 0:
                print("Oi1")
                break
            # either the result comes from the
            # top (K[i-1][w]) or from (val[i-1]
            # + K[i-1] [w-wt[i-1]]) as in Knapsack
            # table. If it comes from the latter
            # one/ it means the item is included.

            if res == K[i - 1][w]:
                print("Oi2")
                continue
            else:
                print("Oi3")
                # This item is included.
                #print(wt[i - 1])
                aux = {"peso":wt[i-1], "valor":val[i-1]}
                resgatados.append(aux)
                
                # Since this weight is included
                # its value is deducted
                res = res - val[i - 1]
                w = w - wt[i - 1]"""

        return res

    def computeKnapsackProblemDynamicProgramming(self, listOfValues, listOfWeights, maxCapacity, n):
        #K = np.array([[0 for x in range(maxCapacity + 1)] for x in range(n + 1)])
        K = [[0 for i in range(maxCapacity + 1)] for j in range(n + 1)]

        for it in range(n + 1):
            for cap in range(maxCapacity + 1):
                if it == 0 or cap == 0:
                    K[it][cap] = 0
                elif listOfWeights[it - 1] <= cap:
                    K[it][cap] = max(listOfValues[it - 1] + K[it - 1][cap - listOfWeights[it - 1]], K[it - 1][cap])
                else:
                    K[it][cap] = K[it - 1][cap]

        return K[n][maxCapacity]


    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """
        
        nextMove = self.move()
        return (nextMove[1], self.goalPos == State(nextMove[0][0], nextMove[0][1]))   
    

    def planoVoltaParaBase(self, agent, motivo):

        if self.currentState.row == 0 and self.currentState.col == 0 and (motivo == "bateria" or motivo == "pacotes"):
            #agent.bateria = agent.bateriaMax
            agent.pacotes = agent.maxPacotes
            agent.custoAtual = 0
            self.voltaParaBase = False
            return "recarregou"

        elif self.currentState.row == 0 and self.currentState.col == 0 and (motivo == "tempo" or motivo == "resgatouTudo"):
            return -1

        else: ##definindo o caminho para voltar para a base
            lista = self.mapa[self.currentState.row, self.currentState.col]['unbacktrackedSocorrista']
            movDirection = self.acaoContraria(self.movePos, lista[0])
            lista.pop(0)
            state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])          

        return movDirection, state


    def isAValidState(self, state):
        """
        verifica se eh possivel ir para este estado
        """


        if state.row < self.maxRows and state.col < self.maxColumns and state.row >= 0 and state.col >= 0:
           return 1

        return 0
    
    def funcUnbacktrack(self, action, state):
        """
            adiciona na lista de funcoes unbacktracked do socorrista
        """

        if(self.isAValidState(state)):
            self.mapa[state.row, state.col]['unbacktrackedSocorrista'].append(action)


    def tryAction(self, action, state):
        """
            armazena a função sucessora aprendida durante a exploração e retorna o
            estado sucessor de s pela execução de a (se conhecido)
        """
        """
            Lista de ações ainda não tentadas no estado s
        """
        """
            Lista de ações ainda não desfeitas no estado s
        """

        ##retira a acao do untried
        if(action in self.estados[self.currentState.row, self.currentState.col]['untriedActions']):
                possibilities = []
                listaAux = self.estados[self.currentState.row, self.currentState.col]['untriedActions']
                for i in range (0, len(listaAux)):
                    if(action != listaAux[i]):
                        possibilities.append(listaAux[i]) 

                self.estados[self.currentState.row, self.currentState.col].update(untriedActions = possibilities)

    def setInfo(self, infoVitimas, mapa):
        """
            adiciona as informacoes
        """
        self.infoVitimas = infoVitimas
        self.mapa = mapa
