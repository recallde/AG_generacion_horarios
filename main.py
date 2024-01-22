# -*- coding: utf-8 -*-

from parametros import Parametros
from algoritmo import AlgoritmoGenetico
from fitness import FitnessFunctions

class Main:

    def __init__(self):
         self.param = Parametros()

    def inicializacionPrimerAG(self, ag1, ftnss, banco_docente, h_min, h_max):
        def wrapper(individual):                                                                    # Este wrapper hace posible pasarle más de un argumento a la función fitness
            valor_fitness = ftnss.fit1(individual, False)
            return valor_fitness
        ag1.Inicializacion(ag1.seleccion_Docente , banco_docente, h_min, h_max, None, (-1.0,))
        ag1.Operadores(wrapper, 0.2)

    def inicializacionSegundoAG(self, ind_pasado, A_t_orden, ag2, ftnss, labs_fisicos, disponibilidad, banco_docente):
        def wrapper2(individual):
            valor_fitness2 = ftnss.fit2(individual, ind_pasado, A_t_orden, labs_fisicos, False)
            return valor_fitness2
        ag2.Inicializacion(ag2.seleccion_Franja , ind_pasado, A_t_orden, disponibilidad, banco_docente, (-1.0,))
        ag2.Operadores(wrapper2, 0.1)
    
    def ejecutarAlgoritmos(self, ag, ngen, mu, lambda_, cxpb, mutpb, mostrarEjecucion):
        pop, stats, hof = ag.Ejecucion(ngen, mu, lambda_, cxpb, mutpb, mostrarEjecucion)
        return pop, stats, hof

    def main(self): 

        # Obtener datos de entrada
        banco_docente, h_max, disponibilidad  = self.param.lecturaProyeccion()
        h_ciencias_basc = self.param.lecturaCienciasBasicas()
        asig_totales, h_min = self.param.tratamientoDatos()
        

        # Distribuir asignaturas práticas en los laboratorios fisicos
        labs_fisicos = self.param.divisionLabs(asig_totales)

        # Inicializar clase que contiene la función de aptitud
        fit = FitnessFunctions(asig_totales, h_ciencias_basc, h_min)

        # Crear objetos para el primer algotimo
        algtm1 = AlgoritmoGenetico(asig_totales, h_ciencias_basc)

        # Se ejecuta el primer algoritmo
        self.inicializacionPrimerAG(algtm1, fit, banco_docente, h_min, h_max)
        pop1, stats1, hof1 = self.ejecutarAlgoritmos(algtm1, 90, 25, 150, 0.7, 0.3, True)   # ngen es 30
        fit.fit1(hof1[0], True) # Ver desempeño del hof1

        # Se reorganiza la lista de asig_totales en función de el semestre y los grupos
        A_t_orden, hof1_orden = zip(*sorted(zip(asig_totales, hof1[0]), key=lambda x: (x[0][1], x[0][-1])))
        
        # Crear objetos para el primer algotimo        
        algtm2 = AlgoritmoGenetico(A_t_orden, h_ciencias_basc)

        # Se ejecuta el segundo algoritmo
        self.inicializacionSegundoAG(hof1_orden, A_t_orden, algtm2, fit, labs_fisicos, disponibilidad, banco_docente)
        pop2, stats2, hof2 = self.ejecutarAlgoritmos(algtm2, 700, 65, 750, 0.7, 0.15, True) # ngen es 75 750 900
        fit.fit2(hof2[0], hof1_orden, A_t_orden, labs_fisicos, True) # Ver desempeño del hof2

        self.param.exportarHorarios(hof1_orden, hof2[0], A_t_orden)

if __name__=="__main__":

    for i in range(10):
        print('Iteracion numero: '+ str(i+1))
        principal = Main()
        principal.main()