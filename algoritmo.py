import numpy as np
import random
from deap import base, creator, tools, algorithms

class AlgoritmoGenetico():
     
    def __init__(self, Asig_t, H_cb):
        super().__init__()
        self.toolbox = base.Toolbox()
        self.A_t = Asig_t
        self.i = 0
        self.j = 0
        self.grupo = None
        self.asignatura = None
        self.repetidos = []
        self.franjas = ['L7',  'L9',  'L11',  'L2', 
                        'M7',  'M9',  'M11',  'M2',   
                        'X7',  'X9',  'X11',  'X2',  
                        'J7',  'J9',  'J11',  'J2', 
                        'V7',  'V9',  'V11',  'V2', 
                        'S7',  'S9']
        self.franjas_disponibles = self.franjas.copy()
        self.docente = None
        self.hist_docentes = []
        self.hist_frnj = []
        self.horariosCB = list(H_cb)
        self.acum_frj = []
        self.historico_docentes = []
        self.historico_franjas = []
        self.asignaturas_totales = [(a[0],a[1],a[2]) for a in self.A_t]      

    def seleccion_Docente(self, ind_optns, h_min, h_max, a):                                                                               # Restrición 3 No se puede asignar docentes a cursos que no son de su experticia
                                                                                                                                           # Restrición NUEVA Dentro de un grupo, un curso solo puede ser dictado por un docente
        self.asignaturas_totales = [(a[0],a[1],a[3]) for a in self.A_t]
        asig_eval = self.asignaturas_totales[self.i]
        nmb_d = [a[0] for a in ind_optns]

        def probabilidad_seleccion(docente):
            if (self.hist_docentes.count(docente)*2 < h_min[nmb_d.index(docente)]):
                p = 0.9
            elif (self.hist_docentes.count(docente)*2 > h_min[nmb_d.index(docente)]) and (self.hist_docentes.count(docente)*2 < h_max[nmb_d.index(docente)]):
                p = 0.08
            else: 
                p = 0.02
            return p
         
        if asig_eval in self.hist_frnj:                                                                                                 # Esto hace que en un mismo curso solo pueda hacer un docente
            self.docente = self.hist_docentes[self.hist_frnj.index(asig_eval)]  

        else:        
            self.asignatura = str(self.A_t[self.i][0])
            docentes_asignatura = [docente for docente, asignaturas in ind_optns if self.asignatura in str(asignaturas).split(',') ]        # Esto selecciona a los docentes que pueden dictar x asignatura 
            prob = list(map(probabilidad_seleccion, docentes_asignatura))       
            #print(docentes_asignatura, prob, self.asignatura, asig_eval)  
            self.docente = random.choices(docentes_asignatura, prob, k=1)[0]            
   
        self.hist_docentes.append(self.docente)
        self.hist_frnj.append(asig_eval)

        if self.i == (len(self.A_t)-1):
            self.i = 0
            self.hist_docentes = []
            self.hist_frnj = []
        else:
            self.i += 1
        
        return self.docente
    
    def seleccion_Franja(self, indv_docentes, A_t_orden, disp_D, lista_docentes): #  Restricción 11 Deben existir periodos específicos donde no se puedan asignar clase a determinados cursos

        asig_eval = A_t_orden[self.j]
        docente_eval = indv_docentes[self.j]
        docentes = [a[0] for a in lista_docentes]
        exc_1 = ['M'] #ml
        exc_2 = ['M', '4'] #2m4
        exc_3 = [] # l
        exc_4 = ['4'] # 24

        #--------------------------------------------------------------------------------------------------------------------------------------#
        
        # Reinicio de franjas disponibles cuando se cambia de grupo y sustracción de franjas programadas en ciencias básicas
        if self.grupo != asig_eval[-1]:
            self.grupo = asig_eval[-1]
            #print('\n')
            self.franjas_disponibles = self.franjas.copy()
            franja_CB =  [h for h in self.horariosCB if h[0] == asig_eval[-1] and h[1] == asig_eval[1]]
            if franja_CB: 
                self.franjas_disponibles = list(set(self.franjas_disponibles) - set(franja_CB[0][2]) )
            self.repetidos = []

        # Esta restricción evita que a un docente se le asigne la misma franja más de dos veces
        franjas_ya_ocupadas = [franjas for d, franjas in zip(self.historico_docentes, self.historico_franjas) if d == docente_eval]

        # Esta restricción evita que se asignen franjas fuera de la disponibilidad del docente
        franjas_disp_d = str(disp_D[docentes.index(docente_eval)]).split(',')
         
        # Dependiendo del tipo de asignatura, se le asignan diferentes grupos de franjas horarias disponibles
        if asig_eval[1] in [1,2,3,4] and ('Lab' in asig_eval[0]):                                                                                                                                                  # No asignar mañanas, ni martes, ni lunes a labs de primeros semestres
            franjas_lab10caj = list(filter(lambda f: all(exc not in f for exc in exc_1), self.franjas_disponibles))
        elif asig_eval[1] in [1,2,3,4] and ('Lab' not in asig_eval[0]):                                                                                                                                            # No asignar clase en las tardes ni martes a las teóricas de primeros semestres
            franjas_lab10caj = list(filter(lambda f: all(exc not in f for exc in exc_2), self.franjas_disponibles))
        elif asig_eval[1] in [5,6,7,8,9,10] and ('Lab' in asig_eval[0]):                                                                                                                                           # No asignar clase en la mañana ni los lunes a los labs de semestres superiores
            franjas_lab10caj = list(filter(lambda f: all(exc not in f for exc in exc_3), self.franjas_disponibles))
        elif asig_eval[1] in [5,6,7,8,9,10] and ('Lab' not in asig_eval[0]):                                                                                                                                       # No asignar clase en las tardes a asignaturas teórics de semestres superiores
            franjas_lab10caj = list(filter(lambda f: all(exc not in f for exc in exc_4), self.franjas_disponibles)) 
        else:                                                               
            franjas_lab10caj = self.franjas_disponibles

        franjas_sin_ocup = list((set(franjas_lab10caj) - set(franjas_ya_ocupadas)))
        franjas_finales = list(set(franjas_sin_ocup) & set(franjas_disp_d))  

        if len(franjas_lab10caj) == 0:
            franjas_para_escoger = self.franjas_disponibles
        elif len(franjas_sin_ocup) == 0:
            franjas_para_escoger = franjas_lab10caj
        elif len(franjas_finales) == 0:
            franjas_para_escoger = franjas_sin_ocup
        else:
            franjas_para_escoger = franjas_finales

        cnt_while = 0
        while True:  # Este while revisa si a una asignatura de un grupo se le va a asignar un día que ya fue asignado a la misma asignatura, de modo que una asignatura no se asigne dos veces un mismo día
            franja = random.choice(franjas_para_escoger)
            historico = asig_eval[0]+f"{asig_eval[-1]}"+franja[0]
            cnt_while += 1
            if historico not in self.acum_frj or cnt_while>2:
                self.acum_frj.append(asig_eval[0]+f"{asig_eval[-1]}"+franja[0]) # Vector que va guardando el curso, grupo y dia al que fue asignado
                break

        # Hace que no se le asignen horarios estrictamente despues de mecanizado y tecnologia a las porximas asignaturas
        if asig_eval[0] in ['Lab Proc. De Mecanizado', 'Lab Tecnologia Mecanica'] and int(franja[1:]) != 11:
            franja_siguiente = f"{franja[0]}{int(franja[1:])+2}"
            self.repetidos.append(franja_siguiente)
           # print(franja_siguiente, franja)


        # Esta condicion hace posible que si a una asignatura ya se le asignó una franja, dicha franja no se le podrá asignar a otra asignatura del mismo grupo
        self.repetidos.append(franja)
        self.historico_docentes.append(docente_eval)
        self.historico_franjas.append(franja)

        # Minimizar clase al medio dia está implicita

        self.franjas_disponibles = [f for f in self.franjas_disponibles if f not in self.repetidos]

        if self.j == (len(self.A_t)-1):
            self.j = 0
            self.acum_frj = []
            self.historico_docentes = []
            self.historico_franjas = []        
        else:
            self.j += 1 

        return franja

    def Inicializacion(self, fun_creacion, ind, h_min, h_max, lista_docentes, fitness_weights):

        creator.create("FitnessMin", base.Fitness, weights= fitness_weights) 
        creator.create("Individuo", list, fitness=creator.FitnessMin)                                                               # type: ignore

        self.toolbox.register("aleatorio", fun_creacion, ind, h_min, h_max, lista_docentes)
        self.toolbox.register("individuo", tools.initRepeat, creator.Individuo, self.toolbox.aleatorio, n=len(self.A_t))            # type: ignore
        self.toolbox.register("poblacion", tools.initRepeat, list, self.toolbox.individuo)                                          # type: ignore

    def Operadores(self, fitness, mutatepb):

        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutShuffleIndexes, indpb = mutatepb)
        self.toolbox.register("select",  tools.selBest )
        self.toolbox.register("evaluate", fitness)

    def Ejecucion(self, mu, ngen, lambda_, cxpb, mutpb, flag):

        pop = self.toolbox.poblacion(mu)                                                                                           # type: ignore      
        hof = tools.HallOfFame(3) 
        stats = tools.Statistics(key=lambda ind: ind.fitness.values)                                                               # type: ignore
        stats.register("avg", np.mean)
        stats.register("min", np.min)  

        pop, logbook = algorithms.eaMuPlusLambda(pop, self.toolbox, mu, lambda_ , cxpb, mutpb, ngen, stats=stats, halloffame = hof, verbose = flag)
        #pop, logbook = algorithms.eaSimple(pop, self.toolbox, 0.7, 0.1, ngen, stats=stats, halloffame = hof, verbose = flag)
        #pop, logbook = algorithms.eaMuCommaLambda(pop, self.toolbox, mu, lambda_ , cxpb, mutpb, ngen, stats=stats, halloffame = hof, verbose = flag)
    
        return pop, stats, hof