from parametros import Parametros
import numpy as np

class FitnessFunctions(Parametros):
   
    def __init__(self, A_t, H_cb, horas_min):

        super().__init__()
        super().lecturaProyeccion()
        if not isinstance(A_t, list):
            raise ValueError("El argumento 'cursos' debe ser una lista")
        self.A_t = A_t
        self.horarios_cb = list(H_cb)
        self.horas_min = horas_min       

    def fit1(self, individuo, flag):

        # Restrición 1 Los docentes deben dictar asignaturas dentro de las cátedras que se les han asignado.
        fuera_de_horario = [(i, a) for i, a in zip(individuo, self.A_t) if a[0] not in self.DA[self.D.index(i)].split(',')]
        cont_expt = len(fuera_de_horario) 

        # Restrición 2 Los docentes deben cumplir con una cantidad de horas asignadas por semana.
        indices_docentes = [self.D.index(d) for d in individuo]
        horas_actuales = np.zeros(len(self.D))
        np.add.at(horas_actuales, indices_docentes, np.array(self.A_t)[:, 2].astype(float))                                                                                                      # Se van sumando las horas de los cursos que tienen un mismo docente en horas_actuales para saber cuantas horas da un profesor a la semana.
        individuos_horas_superadas = [(ac, d) for ac, hmin, hmax, d in zip(horas_actuales, self.horas_min, self.HD, self.D) if not (hmin <= ac <= hmax)]                                # De esta resta se suman los resultados positivos para saber cuantas horas faltan en total.
        cnt_horas_superadas = len(individuos_horas_superadas)   
                                                                                                              
        # Restricción 3 Solo un docente puede impartir una asignatura dentro de un grupo 
        curso_grupo = [(t[0],t[-1]) for t in self.A_t]                                                                                                                                 # Los grupos son aislados para ser contenidos en un solo vector exclusivo de grupos.
        curso_grupo_docente = [(t[0], t[-1], i) for t, i in zip(self.A_t, individuo)] 
        cnt_mezcla = (list(map(lambda a,b: False if curso_grupo.count(a) == curso_grupo_docente.count(b) else True ,curso_grupo, curso_grupo_docente )))
        ctm = sum(cnt_mezcla)

        fitness_val = [cont_expt, cnt_horas_superadas, ctm]

        if flag:
            print(fitness_val)

        return sum(fitness_val),
    
    def fit2(self, individuo, mejor_individuo_pasado, A_t_orden, lab_fisico, flag):
        
        indv_pasado = mejor_individuo_pasado

        # Restricción 4 Los docentes no deben tener dos o más asignaturas asignadas en una misma franja horaria 
        docente_periodo = list(zip(indv_pasado, individuo))                                                                                                                                           # Se une el individuo de docentes que contiene los docentes con el nuevo que contienen los periodos
        docentes_con_cruce =  [elem for elem in set(docente_periodo) if docente_periodo.count(elem) > 1]                                                                           # Se busca los elementos de docente_periodo que se repiten dos o más veces

        # Restricción 5 Los docentes deben tener franjas asignadas dentro de su disponibilidad horaria 
        indices_docentes = [self.D.index(docente) for docente in indv_pasado]                                            
        docente_fuera_de_horario = [self.D[d] for d, i in zip(indices_docentes, individuo) if i not in self.FD[d]]
        
        # Restricción 6 Una asignatura solo se puede dictar una vez al día  (Excepcion para las asig de 3h)
        curso_grupo_dia = [c[0] + f"{c[-1]}" + f[0] for c, f in zip(A_t_orden, individuo) if c[0] not in self.asig_3h]                                                                        
        cursos_repetidos_dia = [elem for elem in set(curso_grupo_dia) if curso_grupo_dia.count(elem) > 1]  

        # Restricción 7 Una asignatura no debe ser asignada en la misma franja horaria que otra  
        semestre_grupo = [(c[1], c[-1], t) for c, t in zip(A_t_orden, individuo)]
        cruces_dentro_grupo = [elem for elem in set(semestre_grupo) if semestre_grupo.count(elem) > 1]

        # Restricción 7 Una asignatura no debe ser asignada en la misma franja horaria que otra (Caso, evitar cruces con asignaturas de 3h) 
        cursos_de_3h = [(c, i) for c, i in zip(A_t_orden, individuo) if c[0] in self.asig_3h]
        def condicion(pr):
                busqueda = f"{pr[1][0]}{int(pr[1][1:])+2}"
                indv_nuevo = [i for c, i in zip(A_t_orden, individuo) if c[1] == pr[0][1] and c[-1] == pr[0][-1]]
                return busqueda in indv_nuevo             
        cruce_bloques_3h = [c for c in cursos_de_3h if condicion(c)]

        cruces = cruces_dentro_grupo + cruce_bloques_3h

        # Restricción 8 Las asignaturas prácticas que se dicten en un mismo laboratorio físico no pueden compartir franjas horarias
        cruce_lab_fisico = []
        for labs in lab_fisico:
            asig_practicas = [i for a, i in zip(A_t_orden, individuo) if a in labs]
            cruces_lab_fisico = [elem for elem in set(asig_practicas) if asig_practicas.count(elem) > 1]
            cruce_lab_fisico.extend(cruces_lab_fisico)
                                                     
        # Restricción 9 Cruces con CB
        asignaturas_inferiores = [ (a, i) for a, i in zip(A_t_orden, individuo) if a[1] in [1,2,3,4,5,6]]
        cruces_cb9 = [a[0] for a in asignaturas_inferiores if a[1] in [hcb[2] for hcb in self.horarios_cb if hcb[0] == a[0][-1] and hcb[1] == a[0][1]]]

        # Restricción 9 Cruces con CB (caso de asig de 3h)        
        def condicion2(x):
            busqueda2 = f"{x[1][0]}1" if int(x[1][1:]) == 11 else f"{x[1][0]}{int(x[1][1:])+2}"
            indv_nuevo2 = [hcb for hcb in self.horarios_cb if hcb[0] == x[0][-1] and hcb[1] == x[0][1]]
            return busqueda2 in indv_nuevo2
        cruce_3h_cb = [c for c in cursos_de_3h if condicion2(c)]

        cruces_cb = cruces_cb9 + cruce_3h_cb

       # Restricción 10 Las asignaturas que pertenezcan a semestres de primer a cuarto semestre no deben ser programas el día martes.
        def condicion4(asig, ind):
            if (asig[1] in [1,2,3,4]) and ('M' in ind):                                                  # No asignar mañanas, ni martes, ni lunes a labs de primeros semestres
                cont = 1 
            else:
                cont = 0
            return cont          
        cruce_cajica = [(a, i) for a, i in zip(A_t_orden, individuo) if condicion4(a, i)]

        # Restricción No Funcional 1 Los horarios de un curso en un mismo semestre no pueden coincidir en un grupo diferente. 
        curso_semestre = [(c[0], c[2], t) for c, t in zip(A_t_orden, individuo)]
        cruces_entre_grupos = [elem for elem in set(curso_semestre) if curso_semestre.count(elem) > 1]                                                                                   
 
        # Restricción No Funcional 2 y 3 NUEVA Evitar labs los lunes y asignaturas teóricas en las tardes
        def condicion3(asig, ind):
            if ('Lab' in asig[0]) and ('L' in ind):                                                  # No asignar mañanas, ni martes, ni lunes a labs de primeros semestres
                cont = 1
            elif asig[1] in [5,6,7,8,9,10] and (('2' in ind) or ('4' in ind)):                                            # No asignar clase en las tardes ni martes a las teóricas de primeros semestres
                cont = 1
            else:
                cont = 0
            return cont          
        lab_lun_teorica_tarde = [(a, i) for a, i in zip(A_t_orden, individuo) if condicion3(a, i)]

        # Restricción No Funcional 5
        grupo_franja = [(c[1], t) for c, t in zip(self.A_t, individuo)]
        franjas_sobrecargadas = [elem for elem in set(grupo_franja) if grupo_franja.count(elem) > 2] 

        restricciones_fun =   [docentes_con_cruce , docente_fuera_de_horario , cursos_repetidos_dia , cruces , cruce_lab_fisico, cruces_cb , cruce_cajica]
        restricciones_nofun = [cruces_entre_grupos, lab_lun_teorica_tarde, franjas_sobrecargadas]
        
        restricciones_totales =  [float(len(elemento)) for elemento in (restricciones_fun + restricciones_nofun)]

        # Esta condición es para visualizar el desempeño del mejor individuo
        if flag: # acá va flag
            print(restricciones_totales,'\n')

        # Pesos
        restricciones_totales[0] *= 1
        restricciones_totales[1] *= 1
        restricciones_totales[2] *= 1
        restricciones_totales[3] *= 1
        restricciones_totales[4] *= 1
        restricciones_totales[5] *= 1
        restricciones_totales[6] *= 1
        restricciones_totales[7] *= 0.7
        restricciones_totales[8] *= 0.7
        restricciones_totales[9] *= 0.7
        
        return sum(restricciones_totales),