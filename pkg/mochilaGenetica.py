from random import randint, choice, random

class MochilaGenetica:
    def __init__(self, capacidade, infoVitimas):
        self.capacidade = capacidade
        self.infoVitimas = infoVitimas

    def genetico(self):
        quantItens = len(self.infoVitimas)
    
        tamPopulacao = 20

        populacao = self.criaPopulacao(tamPopulacao, quantItens)
        
        print("POPULAÇÂO:")
        for p in populacao:
            print(p)

        geracao = 1 #geracao atual

        historicoFitness = [] #lista que guarda o fitness de cada geracao

        while True:

            print("GERACAO", geracao)

            populacao, historicoFitness = self.calculaFitnessPopulacao(populacao, self.capacidade, historicoFitness)

            if geracao > 1000:
                if historicoFitness[geracao-1] == historicoFitness[(geracao-1)//2]:
                    break
            print(len(historicoFitness))
            print(geracao, geracao//2)


            novaGeracao = []
            elite = int(tamPopulacao * 0.1) #apenas 10% (elite) vao para a proxima geracao
            novaGeracao.extend(populacao[:elite])

            #Os 50% mais adequados (fittest) vao reproduzir 
            resto = int(tamPopulacao * 0.9)

            for _ in range(resto):
                pai = choice(populacao[:50])
                mae = choice(populacao[:50])
                filho = self.reproducao(pai, mae)
                novaGeracao.append(filho)

            populacao = novaGeracao
            geracao += 1
        
        melhor = populacao[0]
        return melhor


    def criaIndividuo(self, quant_genes):
        """
            Cria individuo
        """
        individuo = []
        for i in range(0, quant_genes):
           individuo.append(randint(0, 1))
        return individuo

    def criaPopulacao(self, tam_populacao, quant_genes):
        """
            Cria a populacao
        """
        populacao = []
        for i in range(0, tam_populacao):
           populacao.append(self.criaIndividuo(quant_genes))
        return populacao

    def calculaFitnessPopulacao(self, populacao, capacidade, historicoFitness):

        populacaoFitness = []
        vetorFitness = []

        for individuo in populacao:
            valorFitness = self.calculaFitness(individuo, capacidade)
            aux = {'individuo': individuo, "fitness": valorFitness}
            populacaoFitness.append(aux)
            vetorFitness.append(valorFitness)

        #ordena os individuos
        vetorFitness.sort(reverse=True)
        historicoFitness.append(vetorFitness[0])

        index = 0 
        while(len(populacaoFitness) > 0):
            for pop in populacaoFitness:
                if vetorFitness[index] == pop["fitness"]:
                    populacao[index] = pop["individuo"]
                    populacaoFitness.remove(pop)
                    index +=1
                    break

        return populacao, historicoFitness


    def calculaFitness(self, individuo, capacidade):
        """
            Calcula a avaliacao de um individuo
        """
        pesoTotal = 0
        valorTotal = 0
        for indice, valor in enumerate(individuo):
            #print(indice)
            pesoTotal += (individuo[indice] * self.infoVitimas[indice]["tempoAcesso"])
            valorTotal += (individuo[indice] * self.infoVitimas[indice]["gravidade"])


        if (capacidade - pesoTotal) < 0:
            return -1 #retorna -1 no caso de peso excedido 

        return valorTotal #se for um individuo valido retorna seu valor, sendo maior melhor


    def mutacao(self):
        gene = randint(0, 1)
        return gene


    def reproducao(self, pai, mae):

        prob = random()
        filho = []

        for genePai, geneMae in zip(pai, mae):
                ##entre 0 a 44 = pega gene do pai
                if prob < 0.45:
                    filho.append(genePai)
            
                ##entre 45 a 89 = pega gene da mae
                elif prob < 0.90:
                    filho.append(geneMae)
    
                ##90 a 100 sofre mutacao
                else:
                    filho.append(self.mutacao())

        return filho


    def calculaGravidadeVitimas(self, infoVitimas):
    
        for vit in infoVitimas:
            sinais = vit["sinaisVitais"][0]
            ultimoIndex = len(sinais)-1
            vit["gravidade"] = sinais[ultimoIndex] 
                
            difAcesso = vit["difAcesso"][0]
            ultimoIndex = len(difAcesso)-1
            vit["tempoAcesso"] = int(difAcesso[ultimoIndex])
         