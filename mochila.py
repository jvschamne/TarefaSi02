from random import randint

def criaItens(quantidade):
    valores = []
    pesos = []
    for i in range (0, quantidade):
        valor = randint(1, 10)
        peso = randint(1, 10)
        valores.append(valor)
        pesos.append(peso)

    return valores, pesos


def mochila(quantItens, pesos, valores, capacidade):
    mochila = [[0 for i in range(capacidade+1)] for j in range(quantItens+1)]

    for n in range(quantItens + 1):
        for cap in range(capacidade + 1):
            if n == 0 or cap == 0:
                mochila[n][cap] = 0
            elif pesos[n - 1] <= cap:
                print("n={}, cap{}".format(n, cap))
                print("mochila n cap = ", mochila[n][cap])
                mochila[n][cap] = max(valores[n - 1] + mochila[n - 1][cap - pesos[n - 1]], mochila[n - 1][cap])
            else:
                mochila[n][cap] = mochila[n - 1][cap]


    return mochila[quantItens][capacidade]


def main():
    capacidade = 10
    pesos, valores = criaItens(10)
    quantItens = len(pesos)

    for p, v in zip(pesos, valores):
        print("Peso:", p, "Valor:", v)

    resultado = mochila(quantItens, pesos, valores, capacidade)
    print("Resultado=", resultado)


if __name__ == '__main__':
    main()