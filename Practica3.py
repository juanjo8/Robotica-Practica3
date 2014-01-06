# -*- encoding: utf-8 -*-
from pyrobot.brain import Brain
import random


class Individuo:
    def __init__(self, IndId):
        # Constantes
        self.CONTROL_BORROSO_SIZE = 12  # tamaño del array controlBorroso

        # Variables
        self.id = IndId  # Id para diferenciar un individuo de otro
        self.calidad = 0  # calidad del individuo
        self.controlBorroso = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.initControlBorroso()  # array con la funcion de pertenencia [X,X,X,Y,Y,Y,Z,Z,Z,Z,Z,Z] X = Error Y = D.Error Z = Salida
        self.probabilidad = 0  # probabilidad de ser elegido en la mutación

    def initControlBorroso(self):
        # Error
        aux = [random.random() for col in range(3)]
        aux.sort()  # ordenamos para que los puntos de corte de la funcion de pertenencia esten ordenados
        self.controlBorroso[0] = aux[0]
        self.controlBorroso[1] = aux[1]
        self.controlBorroso[2] = aux[2]

        # Derivada del error
        aux = [random.random() for col in range(3)]
        aux.sort()  # ordenamos para que los puntos de corte de la funcion de pertenencia esten ordenados
        self.controlBorroso[3] = aux[0]
        self.controlBorroso[4] = aux[1]
        self.controlBorroso[5] = aux[2]

        # Salida
        aux = [random.random() for col in range(6)]
        aux.sort()  # ordenamos para que los puntos de corte de la funcion de pertenencia esten ordenados
        self.controlBorroso[6] = aux[0]
        self.controlBorroso[7] = aux[1]
        self.controlBorroso[8] = aux[2]
        self.controlBorroso[9] = aux[3]
        self.controlBorroso[10] = aux[4]
        self.controlBorroso[11] = aux[5]


class Control(Brain):

    def setup(self):
        # Constantes
        self.MAX_GEN = 100
        self.MAX_ITR = 1500
        self.MAX_IND = 20

        # Variables
        self.itr = 0  # numero de iteraciones que ha relizado el robot hasta ahora
        self.gen = 0  # generacion en la que estamos
        self.ind = 0  # individuo en el que estamos
        self.poblacion = range(0, self.MAX_IND)
        self.probTotal = 0
        self.elite = Individuo(-1)
        self.initPoblacion()

    # Inicializa la primera poblacion que se usara con individuos
    def initPoblacion(self):
        # Inicializamos la primera población
        for i in range(self.MAX_IND):
            self.poblacion[i] = Individuo(i)
            self.poblacion[i].calidad = 1  # Para que no crashe por dividir entre 0 mas adelante
            self.probTotal = self.probTotal + self.poblacion[i].calidad

            # Elitismo
            if (i == 0):
                self.elite = self.poblacion[i]
            elif (self.elite.calidad < self.poblacion[i].calidad):
                self.elite = self.poblacion[i]

        # Asignamos la probabilidad que tiene de ser elegido cuando se vaya a mutar.
        for i in range(self.MAX_IND):
            self.poblacion[i].probabilidad = float((self.poblacion[i].calidad) / self.probTotal)

    # Asigna calidad a un individuo
    def setCalidad(self):
        return self.MAX_ITR / self.itr

    # Crea una nueva poblacion de individuos mutandolos.
    def nuevaPoblacion(self):
        # El primer individuo el mejor de la generacion anterior
        nuevapoblacion = range(0, self.MAX_IND)
        nuevapoblacion[0] = self.elite

        # Creamos la "ruleta" de probabilidades
        tablaProb = range(0, self.MAX_IND)
        probAcum = 0  # Probabilidad acumulada hasta el momento.
        for i in range(0, self.MAX_IND):
            probAcum = probAcum + self.poblacion[i].probabilidad
            tablaProb[i] = [self.poblacion[i].id, probAcum]

        # Mutamos los individuos y los añadimos a la nueva poblacion
        for i in range(1, self.MAX_IND):
            prob = random.random()

            pos = 0  # elemento de la tabla que ha "tocado"
            # Buscamos el individuo en la tabla
            for j in range (0, self.MAX_IND):
                if (prob < tablaProb[j][1]):
                   pos = j

            newIndividuo = self.poblacion[pos]
            newIndividuo.id = tablaProb[pos][0]
            newIndividuo.muta()

            nuevapoblacion[i] = newIndividuo

    # Asigna un elite en la poblacion
    def setElite(self):
        for i in range(0, self.MAX_IND):
            if (self.poblacion[i].calidad > self.elite.calidad):
                self.elite = self.poblacion[i].calidad

    def step(self):
        if self.itr == self.MAX_ITR or self.luzEncontrada():
            self.poblacion[self.ind].calidad = self.setCalidad()
            self.itr = 0
            self.ind = self.ind + 1
            self.posiciona()  # ha de ser una funcion que entre 4 o 5 puntos aleatorios seleccione uno y fije el robot.
            if self.ind == self.MAX_IND:
                self.ind = 0
                self.gen = self.gen + 1
                self.setElite()
                if self.gen == self.MAX_GEN:
                    done = 1
                else:
                    self.nuevaPoblacion()
        else:
            t, r = self.determineMove()
            self.robot.move(t, r)
            self.itr = self.itr + 1


def INIT(engine):
    assert (engine.robot.requires("range-sensor")
            and engine.robot.requires("continuous-movement"))
    return Control('Control', engine)