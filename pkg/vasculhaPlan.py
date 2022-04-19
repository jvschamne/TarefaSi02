from random import randint
from state import State
from time import sleep


class VasculhaPlan:
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
        self.estados = {} #dicionario
        self.acaoPadrao = 0
        self.visitados = 1
        self.voltaUmaPosicao = 0
        self.voltaParaBase = False
        self.estadosPossiveis = 0

        self.possibilities = ["N", "S", "L", "O", "NE", "NO", "SE", "SO"]
        self.movePos = { "N" : (-1, 0),
                    "S" : (1, 0),
                    "L" : (0, 1),
                    "O" : (0, -1),
                    "NE" : (-1, 1),
                    "NO" : (-1, -1),
                    "SE" : (1, 1),
                    "SO" : (1, -1)}
 
     
        ##inicializa dicionario que armazena os estados
        for linha in range (0, self.maxRows):
            for coluna in  range (0, self.maxColumns): 
                aux = (linha, coluna)
                atributos = {"type": "", "visited": False, "unbacktrackedActions": [], "untriedActions": self.possibilities, "successActions": [], "distanciaDaBase": 9999999, "revisitado": False, "unbacktrackedSocorrista": []} 
                self.estados[aux] = atributos    ## setando o default como nenhuma (no operation)

        self.estados[self.initialState.row, self.initialState.col]["distanciaDaBase"] = 0


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
        if (delta_row != 0 and delta_col != 0):
            if (self.currentState.row + delta_row, self.currentState.col) in self.walls and (self.currentState.row, self.currentState.col + delta_col) in self.walls:
                return False
        
        return True

    def decideNextPosition(self, agent):
         """ Sorteia uma direcao e calcula a posicao futura do agente 
         @return: tupla contendo a acao (direcao) e o estado futuro resultante da movimentacao """

         """
            este algoritmo funciona como um online DFS modificado
            ele tenta todas as acoes nao tentadas para cada estado, evitando lugares ja visitados
            casa nao haja nenhum estado nao visitado ao seu redor, ele fara um backtracking ate encontrar um estado nao visitado 
         """

        ##tentar a primeira acao da lista de acoes nao tentadas no estado atual        
         try:
                lista = self.estados[self.currentState.row, self.currentState.col]['untriedActions']
                movDirection = lista[0]
                state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                self.tryAction(movDirection, agent)

        ##caso as acao nao tentadas acabem neste estado
         except IndexError: 
                    ##acao padrao -> indice do vetor de possibilidades de movimento (0 a 7)
                    try:
                        movDirection = self.possibilities[self.acaoPadrao] 
                        self.acaoPadrao += 1
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, agent)

                    ##caso a acao padrao seja maior que 7
                    except IndexError:
                        self.acaoPadrao = 0 ##reinicia o valor da acao padrao
                        movDirection = self.possibilities[self.acaoPadrao]
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, agent)

         ##enquanto nao conseguir encontrar um estado que nao foi visitado   
         while self.isAValidState(state) and self.estados[state.row, state.col]['visited'] == True:
                ##tentar a primeira acao da lista de acoes nao tentadas no estado atual   
                try:
                    lista = self.estados[self.currentState.row, self.currentState.col]['untriedActions']
                    movDirection = lista[0]
                    state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                    self.tryAction(movDirection, agent)

                ##esgotaram-se as untriedActions desse estado, faz Backtracking
                except IndexError: 
                    ##gambiarra para voltar uma posicao para iniciar o backtracking
                    if(self.voltaUmaPosicao == 0):
                        movDirection = self.acaoContraria(self.movePos, agent.previousAction)
                        self.voltaUmaPosicao = 1
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, agent)
                        break

                    else:
                        lista = self.estados[self.currentState.row, self.currentState.col]['unbacktrackedActions']
                        movDirection = self.acaoContraria(self.movePos, lista[0])
                        lista.pop(0)
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, agent)
                        break
    
         return movDirection, state


    def acaoContraria(self, movPos, acao):

        acaoContraria = movPos[acao]
        x = acaoContraria[0] * -1
        y = acaoContraria[1] * -1
        acaoContraria = (x, y)
        
        for key, value in movPos.items():
         if acaoContraria == value:
             acaoContraria = key

        return acaoContraria

    def chooseAction(self, agent):
        """ Escolhe o proximo movimento de forma aleatoria. 
        Eh a acao que vai ser executada pelo agente. 
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """
        ##se ja visitou tudo
        if self.visitados >= self.estadosPossiveis:
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "visitouTudo")

        ##se o tempo esta quase na metade -> comecar a voltar
        elif(agent.tempoLivre <= agent.tempoTotal/2 + 2):
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "tempo")
            
        ##se a bateria esta quase na metade -> comecar a voltar
        """elif(agent.bateria <= agent.custoAtual/2 + 2):
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "bateria")"""
        
        ##escolher a proxima acao
        if(self.voltaParaBase == False):
            result = self.decideNextPosition(agent)

            ##achar um estado que seja possivel ir
            while not self.isPossibleToMove(result[1]):
                if(self.isAValidState(result[1])):
                    if(self.estados[result[1].row, result[1].col]['type'] != "parede"):
                        self.estados[result[1].row, result[1].col]['type'] = "parede"
                        self.estadosPossiveis -= 1
                result = self.decideNextPosition(agent)
                
            ##se o estado for livre
            if(self.isAValidState(result[1])):
                self.estados[result[1].row, result[1].col]['type'] = "livre"

            ##salvando as acoes de sucesso, que realmente mudam de posicao
            self.estados[self.currentState.row, self.currentState.col]['successActions'].append(result[0])

            ##marcar o estado como visitado
            self.visitState(result[1], result[0])  
    
            ##adicionar a acao na lista de unbacktracked nesse estado
            self.funcUnbacktrack(result[0], result[1])

        return result


    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """
        
        nextMove = self.move()
        return (nextMove[1], self.goalPos == State(nextMove[0][0], nextMove[0][1]))   
    

    def planoVoltaParaBase(self, agent, motivo):

        ##se o agente chegou na base por acabar a bateria
        if self.currentState.row == 0 and self.currentState.col == 0 and motivo == "bateria":
            agent.bateria = agent.bateriaMax
            agent.custoAtual = 0
            self.voltaParaBase = False
            return "recarregou"

        ##se o agente chegou na base por acabar o tempo ou visitar tudo
        elif self.currentState.row == 0 and self.currentState.col == 0 and (motivo == "tempo" or motivo == "visitouTudo"):
            return -1

        ##definindo o caminho para voltar para a base
        else: 
            lista = self.estados[self.currentState.row, self.currentState.col]['unbacktrackedActions']
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
    

    def visitState(self, state, action):
        ##marca como visitado
         
        if self.estados[state.row, state.col]['visited'] == False:
            self.visitados += 1
            self.estados[state.row, state.col]['visited'] = True
            distanciaX = state.row - self.initialState.row
            distanciaY = state.col - self.initialState.col
            self.estados[state.row, state.col]['distanciaDaBase'] = distanciaX + distanciaY
            

    def funcUnbacktrack(self, action, state):
        """
            adiciona na lista de funcoes unbacktracked
        """
        if(self.isAValidState(state)):
            self.estados[state.row, state.col]['unbacktrackedActions'].append(action)


    def tryAction(self, action, agent):
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
        ##diminui a bateria
        """if(action in ['N', 'S', 'O', 'L']):
            agent.bateria -= 1

        elif (action in ['NE', 'SE', 'SO', 'NO']):
            agent.bateria -= 1.5"""


        ##retira a acao do untried
        if(action in self.estados[self.currentState.row, self.currentState.col]['untriedActions']):
                possibilities = []
                listaAux = self.estados[self.currentState.row, self.currentState.col]['untriedActions']
                for i in range (0, len(listaAux)):
                    if(action != listaAux[i]):
                        possibilities.append(listaAux[i]) 

                self.estados[self.currentState.row, self.currentState.col].update(untriedActions = possibilities)


    def getMapa(self):
        return self.estados