from random import randint
from state import State
from time import sleep


class vasculhaPlan:
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
        self.inicializacao = False
        self.visitados = 1
        self.voltaUmaPosicao = 0
        self.voltaParaBase = False
        self.estaNaBase = False
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
 
     
         
            ##so vai rodar uma vez, para inicializaro dicionario:
        if(self.inicializacao == False):
                ##inicializa dicionario que armazena os estados
                for linha in range (0, self.maxRows):
                    for coluna in  range (0, self.maxColumns):
                        aux = (linha, coluna)
                        atributos = {"type": "", "visited": False, "takenActions": [], "unbacktrackedActions": [], "untriedActions": self.possibilities, "successActions": [], "distanciaDaBase": 9999999, "revisitado": False, "untriedSocorrista": self.possibilities} 
                        self.estados[aux] = atributos    ## setando o default como nenhuma (no operation)

                self.estados[self.initialState.row, self.initialState.col]["distanciaDaBase"] = 0
                self.inicializacao = True


        
        self.contadorBateria = 0 ##Contador para testar o retorno do agente a base Se contador == 40, volta pra base

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

         if(self.acaoPadrao > 7): 
             self.acaoPadrao = 0

         movDirection = self.possibilities[self.acaoPadrao] 
         state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1]) 
            ##enquanto tem bateria
        
         try:
                lista = self.estados[self.currentState.row, self.currentState.col]['untriedActions']
                movDirection = lista[0]
                state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                self.tryAction(movDirection, state, agent)

         except IndexError:
                    try:
                        movDirection = self.possibilities[self.acaoPadrao] 
                        self.acaoPadrao += 1
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, state, agent)

                    except IndexError:
                        self.acaoPadrao = 0
                        movDirection = self.possibilities[self.acaoPadrao]
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, state, agent)


         while self.isAValidState(state) and self.estados[state.row, state.col]['visited'] == True:## and self.currentState != state and len(self.estados[self.currentState.row, self.currentState.col]['untriedActions']) > 0:
                ##print("ok")
                try:
                    ##print("ok2")
                    lista = self.estados[self.currentState.row, self.currentState.col]['untriedActions']
                    movDirection = lista[0]
                    state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                    self.tryAction(movDirection, state, agent)
                
                except IndexError: ##esgotaram-se as untriedActions desse estado, faz Backtracking
                    if(self.voltaUmaPosicao == 0):
                        movDirection = self.acaoContraria(self.movePos, agent.previousAction)
                        ##print("Volta Uma Posicao, direcao = ", movDirection)
                        self.voltaUmaPosicao = 1
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, state, agent)
                        break

                    else:
                        lista = self.estados[self.currentState.row, self.currentState.col]['unbacktrackedActions']
                        ##print("Unbacktracked = ", lista)
                        movDirection = self.acaoContraria(self.movePos, lista[0])
                        lista.pop(0)
                        state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])
                        self.tryAction(movDirection, state, agent)
                        break
    

         ##print("Diracao de movimento = ", movDirection)
         return movDirection, state


    def acaoContraria(self, movPos, acao):

        acaoContraria = movPos[acao]
        ##print("ACAO CONTRARIOA = ", acaoContraria)
        x = acaoContraria[0] * -1
        y = acaoContraria[1] * -1
        acaoContraria = (x, y)
        
        for key, value in movPos.items():
         if acaoContraria == value:
             acaoContraria = key

        ##print("ACAO CONTRARIOA = ", acaoContraria)
        return acaoContraria

    def chooseAction(self, agent):
        """ Escolhe o proximo movimento de forma aleatoria. 
        Eh a acao que vai ser executada pelo agente. 
        @return: tupla contendo a acao (direcao) e uma instância da classe State que representa a posição esperada após a execução
        """
        ##se esta na base
        print("Distancia da Base:",  self.estados[self.currentState.row, self.currentState.col]["distanciaDaBase"]+2)

        if self.visitados >= self.estadosPossiveis:
            print("VISITADOS = ", self.visitados)
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "visitouTudo")


        elif(agent.tempoLivre <= self.estados[self.currentState.row, self.currentState.col]["distanciaDaBase"]+2):
            print("Tempo restante:", agent.tempoLivre)
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "tempo")
            
        elif(agent.bateria <= agent.custoAtual/2):##self.estados[self.currentState.row, self.currentState.col]["distanciaDaBase"]+2):
            print("Bateria restante:", agent.bateria)
            self.voltaParaBase = True
            result = self.planoVoltaParaBase(agent, "bateria")
        
        if(self.voltaParaBase == False):
            result = self.decideNextPosition(agent)

            while not self.isPossibleToMove(result[1]):
                if(self.isAValidState(result[1])):
                    if(self.estados[result[1].row, result[1].col]['type'] != "parede"):
                        self.estados[result[1].row, result[1].col]['type'] = "parede"
                        self.estadosPossiveis -= 1
                result = self.decideNextPosition(agent)
                
            if(self.isAValidState(result[1])):
                self.estados[result[1].row, result[1].col]['type'] = "livre"

            ##salvando as acoes de sucesso, que realmente mudam de posicao
            self.estados[self.currentState.row, self.currentState.col]['successActions'].append(result[0])

            self.visitState(result[1], result[0])  
    
            self.funcUnbacktrack(result[0], result[1])

        print("VISITADOS = ", self.visitados)
        return result


    def do(self):
        """
        Método utilizado para o polimorfismo dos planos

        Retorna o movimento e o estado do plano (False = nao concluido, True = Concluido)
        """
        
        nextMove = self.move()
        return (nextMove[1], self.goalPos == State(nextMove[0][0], nextMove[0][1]))   
    

##DEFININDO METODOS DO ALGORITMO ONLINE DFS
##OBS: NAO TENHO CERTEZA SE EH MAIS COERENTE COLOCAR ESTES METODOS NA CLASSE NEWPLAN OU AGENTRND

    def planoVoltaParaBase(self, agent, motivo):
        movePos = { "N" : (-1, 0),
                    "S" : (1, 0),
                    "L" : (0, 1),
                    "O" : (0, -1),
                    "NE" : (-1, 1),
                    "NO" : (-1, -1),
                    "SE" : (1, 1),
                    "SO" : (1, -1)}

        sleep(0.1)
        
        print("Base fica na posicao:", self.initialState.row, self.initialState.col)
        print("Posicao Atual:", self.currentState.row, self.currentState.col)
        print("Bateria:", agent.bateria)

        if self.currentState.row == 0 and self.currentState.col == 0 and motivo == "bateria":
            print("Bateria:", agent.bateria)
            ##sleep(3000)
            agent.bateria = agent.bateriaMax
            agent.custoAtual = 0
            self.voltaParaBase = False
            return "recarregou"

        elif self.currentState.row == 0 and self.currentState.col == 0 and (motivo == "tempo" or motivo == "visitouTudo"):
            print("Tempo:", agent.tempoLivre)
            return -1

        else: ##definindo o caminho para voltar para a base
            lista = self.estados[self.currentState.row, self.currentState.col]['unbacktrackedActions']
            movDirection = self.acaoContraria(self.movePos, lista[0])
            lista.pop(0)
            state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])


           # movDirection = 'N'
            #state = State(self.currentState.row + self.movePos[movDirection][0], self.currentState.col + self.movePos[movDirection][1])

        print("\nVolta para base, acao = ", movDirection)             

        return movDirection, state

    def isAValidState(self, state):
        """
        verifica se eh possivel ir para este estado
        """


        if state.row < 25 and state.col < 25 and state.row >= 0 and state.col >= 0:
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
        if(self.isAValidState(state)):
            self.estados[state.row, state.col]['unbacktrackedActions'].append(action)


    def tryAction(self, action, state, agent):
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
        if(action in ['N', 'S', 'O', 'L']):
            agent.bateria -= 1

        elif (action in ['NE', 'SE', 'SO', 'NO']):
            agent.bateria -= 1.5

        ##adiciona acao no takenActions
        self.estados[self.currentState.row, self.currentState.col]['takenActions'].append(action)
        
        ##if(self.isAValidState(state)):
         ##   self.estados[state.row, state.col]['unbacktrackedActions'].append(action)

        ##retira a acao do untried
        if(action in self.estados[self.currentState.row, self.currentState.col]['untriedActions']):
                possibilities = []
                listaAux = self.estados[self.currentState.row, self.currentState.col]['untriedActions']
                for i in range (0, len(listaAux)):
                    if(action != listaAux[i]):
                        possibilities.append(listaAux[i]) 

                ##print(possibilities)
                self.estados[self.currentState.row, self.currentState.col].update(untriedActions = possibilities)
                ##print(action, "removido = ", self.estados[self.currentState.row, self.currentState.col]['untriedActions'])


    def getMapa(self):

        return self.estados
