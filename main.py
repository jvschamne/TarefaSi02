from statistics import mode
import sys
import os
import time

## Importa as classes que serao usadas
sys.path.append('pkg')
from model import Model
from agentVasculhador import AgentVasculhador
from agentSocorrista import AgentSocorrista

## Metodo utilizado para permitir que o usuario construa o labirindo clicando em cima
def buildMaze(model):
    model.drawToBuild()
    step = model.getStep()
    while step == "build":
        model.drawToBuild()
        step = model.getStep()
    ## Atualiza o labirinto
    model.updateMaze()

def main():
    # Lê arquivo config.txt
    arq = open(os.path.join("config_data","config.txt"),"r")
    configDict = {} 
    for line in arq:
        ## O formato de cada linha é:var=valor
        ## As variáveis são 
        ##  maxLin, maxCol que definem o tamanho do labirinto
        ## Tv e Ts: tempo limite para vasculhar e tempo para salvar
        ## Bv e Bs: bateria inicial disponível ao agente vasculhador e ao socorrista
        ## Ks :capacidade de carregar suprimentos em número de pacotes (somente para o ag. socorrista)

        values = line.split("=")
        configDict[values[0]] = int(values[1])

    print("dicionario config: ", configDict)
    # Cria o ambiente (modelo) = Labirinto com suas paredes
    mesh = "square"

    ## nome do arquivo de configuracao do ambiente - deve estar na pasta <proj>/config_data
    loadMaze = "ambiente"

    model = Model(configDict["maxLin"], configDict["maxCol"], mesh, loadMaze)
    buildMaze(model)

    model.maze.board.posAgent
    model.maze.board.posGoal
    # Define a posição inicial do agente no ambiente - corresponde ao estado inicial
    model.setAgentPos(model.maze.board.posAgent[0],model.maze.board.posAgent[1])
    model.setGoalPos(model.maze.board.posGoal[0],model.maze.board.posGoal[1])
  
    model.draw()
    
    # Cria o agente vasculhador
    agent = AgentVasculhador(model, configDict)
    agent.plan.estadosPossiveis = configDict["maxLin"] * configDict["maxCol"]
    
    startVasculhador = time.time()

    ## Ciclo de raciocínio do agente vasculhador
    agent.deliberate()
    while agent.deliberate() != -1:
        model.draw()
        #time.sleep(0.01) # para dar tempo de visualizar as movimentacoes do agente no labirinto
    

    endVasculhador = time.time()
    tempoVasculhador = endVasculhador - startVasculhador

    #pegando o mapa do vasculhador para passar para o socorrista
    mapa = agent.plan.getMapa()

    #pegando as informacoes das vitimas que vasculhador achou para passar para o socorrista
    infoVitimas = agent.getInfoVitimas()
    vitimasEncontradas = len(infoVitimas)
    ##Mudando para o agente socorrista
    agentSocorrista = AgentSocorrista(model, mapa, infoVitimas, configDict)
    agentSocorrista.plan.setInfo(infoVitimas, mapa)


    ##Mudando a cor do agente socorrista em todos os estados (socorrista = azul)
    for i in range(0, model.maze.maxRows):
        for j in range(0, model.maze.maxColumns):
            model.view.board.listPlaces[i][j].changeAgent("S")
    
    startSocorrista = time.time()

    ## Ciclo de raciocínio do agente socorrista
    agentSocorrista.deliberate()
    while agentSocorrista.deliberate() != -1:
        model.draw()
        #time.sleep(0.01) # para dar tempo de visualizar as movimentacoes do agente no labirinto

    endSocorrista = time.time()
    tempoSocorrista = endSocorrista - startSocorrista

    print("Vitimas encontradas = ", vitimasEncontradas)
    print("Vitimas socorridas = ", agentSocorrista.plan.vitimasSalvas)
    print("Tempo do vasculhador= {:.3f} segundos".format(tempoVasculhador))
    print("Tempo do socorrista= {:.3f} segundos".format(tempoSocorrista))
    model.draw()    
        
if __name__ == '__main__':
    main()
