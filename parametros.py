# -*- coding: utf-8 -*-
import itertools
import pandas as pd
import re
import random

class Parametros:
    
    def __init__(self):

        self.ruta_archivo = 'Data/PROYECCION HORARIO INGENIERÍA EN MECATRONICA_2023_2.xlsx'
        self.ruta_archivo_CB = 'Data/MECATRONICA2023_2.xlsx'

        self.primera_hoja_excel = 'Planeacion por materias'
        self.segunda_hoja_excel = 'Horas disponibles docentes'

        self.formato_columnas = {'NOMBRE DE ASIGNATURA': str, 'SEMESTRE': int, 'GRUPO DE ACTIVIDAD': str, 'Número de Horas': int}
        self.formato_columnas2 = {'Cont': int, 'Nombre de profesor': str, 'Horas disponibles 2021-2': int, 'Días disponible': str, 'Cátedras asignadas': str}

        self.encabezados1 = ['NOMBRE DE ASIGNATURA', 'SEMESTRE', 'GRUPO DE ACTIVIDAD', 'Número de Horas' ]
        self.encabezados2 = ['Cont', 'Nombre de profesor', 'Horas disponibles 2021-2', 'Días disponible', 'Cátedras asignadas']

        self.dias = {'L': 'LUNES' , 'M': 'MARTES' , 'X': 'MIERCOLES' , 'J': 'JUEVES' , 'V': 'VIERNES' , 'S': 'SABADO' }

        self.asig_3h = ['Lab Proc. De Mecanizado', 'Lab Tecnologia Mecanica']
        #self.MFA = np.ones((27, 9), dtype=int)

        self.columnas =  ['L', 'M', 'X', 'J', 'V', 'S']
        self.filas = ['7', '8', '9', '10', '11', '12' ,'1' ,'2' ,'3' ,'4', '5']
        self.filas_restrc = [ '8', '10', '12', '3' ,'5']

        self.grupos_letras = ['MEC A', 'MEC B', 'MEC C', 'MEC D', 'MEC E', 'MEC F', 'MEC G', 'MEC H', 'MEC I', 'MEC J', 'MEC K', 'MEC L', 'MEC M', 'MEC N']
        
        self.n_filas = 186
      
    def lecturaCienciasBasicas(self):
     
        cb = pd.ExcelFile(self.ruta_archivo_CB)
        
        horariosCB = []
        
        grupo_act = None
        semestre_act = None

        for hoja in cb.sheet_names:

            horarios_grupo = []
            if 'CAJIC' not in str(hoja):
                hoja_actual = cb.parse(hoja)
                semestre_act = int(re.findall(r'\((.*?)\)', str(hoja))[1])                                                             # Obtengo el semestre en el cual estoy leyendo los datos

                for pos, grp in enumerate(self.grupos_letras):                                                                         # Obtengo el grupo en el cual estoy leyendo los datos
                    if grp in str(hoja):
                        grupo_act = pos + 1
            
                fila_dias = None 
                for indice, valores_fila in hoja_actual.iterrows():
                    if 'HORAS' in valores_fila.values:                                                                                 # Ubico la fila en la cual se encuentran los días del horario
                        fila_dias = indice
                        break

                if fila_dias is not None:
                    rango_filas = range(14, 34, 2)
                    rango_columnas = range(3, 8)

                    for cnt_dia, columna in enumerate(rango_columnas):
                        for cnt_franja, fila in enumerate(rango_filas):
                            valor = hoja_actual.iloc[fila, columna]
                            if pd.notnull(valor):
                                if self.filas[cnt_franja] in self.filas_restrc:                                                          # Condición para evitar cruces con bloques de 1 hora programados a las [ '8', '10', '12', '3' ,'5'] y 1, ej. si una asig está a las 8, se dice que está a las 7 para que el algoritmo debe libre el bloque de 7 a 9
                                    frnj = self.columnas[cnt_dia] + str((int(self.filas[cnt_franja])-1))
                                    horarios_grupo.append(frnj)
                                elif self.filas[cnt_franja] == '1':
                                    frnj = self.columnas[cnt_dia] + str((int(self.filas[cnt_franja])+1))
                                    horarios_grupo.append(frnj)
                                else:
                                    frnj = self.columnas[cnt_dia] + self.filas[cnt_franja]
                                    horarios_grupo.append(frnj) 

                    h_grp_sem_frnjs = [(grupo_act, semestre_act, set(horarios_grupo))]
                    horariosCB.extend(h_grp_sem_frnjs)                                                                                # El formato final es [(grupo, semestre, [lista de franjas])]
        
        return horariosCB
                                                
    def lecturaProyeccion(self):

        # Lectura de datos en Excel
        self.df = pd.read_excel(self.ruta_archivo, sheet_name = None, dtype = self.formato_columnas, nrows = self.n_filas)

        # Los datos se van separando y guardando en vectores diferentes para facilitar su uso
        self.data  = self.df[self.primera_hoja_excel][self.encabezados1[:-1]].values.tolist()
        self.A  = self.df[self.primera_hoja_excel][self.encabezados1[0]].values.tolist()
        self.horas_asignatura = self.df[self.primera_hoja_excel][self.encabezados1[-1]].values.tolist()

        self.Contrato = self.df[self.segunda_hoja_excel][self.encabezados2[0]].values.tolist()
        self.D  = self.df[self.segunda_hoja_excel][self.encabezados2[1]].values.tolist()
        self.HD = self.df[self.segunda_hoja_excel][self.encabezados2[2]].values.tolist()
        self.FD = self.df[self.segunda_hoja_excel][self.encabezados2[3]].values.tolist()
        self.DA = self.df[self.segunda_hoja_excel][self.encabezados2[4]].values.tolist()
        self.bancoDAD = list(zip(self.D, self.DA))                                                                                                                                                 # Varaible que contiene el docente con sus respectivas asignaturas de experticia

        return self.bancoDAD, self.HD, self.FD

    def tratamientoDatos(self):

        # Los datos obtenidos en lecturaProyeccion son tratados para dejarlo en un formato adecuado para realizar la verificación de restricciones
        # Dicho formato es (curso, semestre, n_horas, grupo)
        def descomponer_horas(horas):
            r = list(itertools.repeat(2, horas // 2))
            if horas % 2 != 0 or r == 1:
               r.append(1)
            return r    
        def subdividir_asginaturas(asig, horas_n):
            a_rep = []
            rep_c = list(itertools.repeat(asig, len(horas_n)))
            a_rep = list(map(lambda t, h: (t[0], t[1], h, t[-1]), rep_c, horas_n))
            return a_rep

        trato1 = list(map(lambda x: (x[0], x[1], int(x[2].split(".")[1])) , self.data))
        h_new = list(map(descomponer_horas, self.horas_asignatura))
        trato2 = list(map(subdividir_asginaturas,trato1, h_new))
        asig_totales =  list(itertools.chain(*trato2))


        self.nombre_asignatura = [n[0] for n in asig_totales]
        organizador = []
        
        for nombre in self.nombre_asignatura:  # Se organizan las asignaturas en función del número de docentes que las pueden dictar
            cont = 0
            for catedra in self.DA:
                if nombre in str(catedra).split(','):
                    cont +=1
            organizador.append(cont)
        ordenado = [v[1] for v in sorted(zip(organizador,asig_totales))]

        horas_minimas = list(map(lambda c,d:  4 if c == 'CATEDRA' and d >= 4 else 8 if (c =='PLANTA' or c ==' OCASIONAL') and d >= 8 else d, self.Contrato, self.HD))  # Los docentes de planta dictan minimo 8 horas (admin 4) y catedra 4

        return ordenado, horas_minimas

    def divisionLabs(self, A_t):
    
        lab_electro1 = ['Lab. Circuitos electrónicos','Lab__ Topicos Avanzados','Lab. de Microprocesadores','Lab. de sensores','Lab. Digitales','Lab. Electrónica','Lab. de Control Lineal']                     
        lab_electro2 = ['Lab. Circuitos electrónicos','Lab__ Topicos Avanzados','Lab. de Microprocesadores','Lab. de sensores','Lab. Digitales','Lab. Electrónica','Lab. de Control Lineal']
        lab_electro3 = ['Lab. Circuitos electrónicos','Lab__ Topicos Avanzados','Lab. de Microprocesadores','Lab. de sensores','Lab. Digitales','Lab. Electrónica','Lab. de Control Lineal','Laboratorio de Electronica de Pot']
        lab_robotica = ['Lab_ Robotica','Lab_ Inteligencia Artificial','Lab_ Proc. Digital de señales']
        lab_automati = ['Lab__ de Actuadores','Lab. de Control Lineal','Lab__ Comunicaciones','Lab__ Topicos Avanzados','Lab__ Automatizacion']

        laboratorios = [lab_electro1, lab_electro2, lab_electro3, lab_robotica, lab_automati]

        labs_existentes = list(filter(lambda a: a[0] in (lab_electro3 + lab_robotica + lab_automati), A_t))

        for  lab_act in labs_existentes:
            while True:
                lab_asginado = random.choice(laboratorios)
                if lab_act[0] in lab_asginado:
                    lab_asginado.append(lab_act)
                    break
 
        lab_electro1 = lab_electro1[7:]
        lab_electro2 = lab_electro2[7:] 
        lab_electro3 = lab_electro3[8:]
        lab_robotica = lab_robotica[3:]
        lab_automati = lab_automati[5:]

        #print(laboratorios)

        return laboratorios
        
    def exportarHorarios(self, docentes, franjas, asignaturas):

        df = pd.read_excel( self.ruta_archivo, sheet_name = self.primera_hoja_excel)

        # Buscar celdas en función del nombre de la asginatura y el grupo        
        columna1 = self.encabezados1[0]
        columna2 = self.encabezados1[2]
        # Borro los datos que pueden haber
        df[list(self.dias.values())] = None

        def llenar_celdas(d, f, a):  
            dia = self.dias[f[0]]
            hora = f[1:]
            if a[0] in self.asig_3h:
                cnt_horas = 3
            else:
                cnt_horas = a[2]
            grupo = a[1] + a[-1]*0.1
            
            # Ubico las filas
            #print(grupo, a[0])
            indice = df[(df[columna2] == grupo) & (df[columna1] == a[0])].index[0]
            # Añado los horarios
            df.at[indice, dia] = str(hora) + '-' + str(int(hora) + int(cnt_horas))
            df.at[indice, 'DOCENTE RESPONSABLE'] = d
        list(map(llenar_celdas, docentes, franjas, asignaturas ))
        
        with pd.ExcelWriter(self.ruta_archivo, mode = 'a', engine = 'openpyxl', if_sheet_exists = 'overlay') as writer:
            df.to_excel(writer, sheet_name = self.primera_hoja_excel, index = False)  
        #print(docentes)  
        

        
        
