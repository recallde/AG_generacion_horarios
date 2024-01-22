import numpy as np
import pandas as pd
from parametros import Parametros

class Visualizacion(Parametros):

    def __init__(self, asig_totales):
        super().__init__()
        if not isinstance(asig_totales, list):
            raise ValueError("El argumento 'asig_totales' debe ser una lista")
        self.filas = ['07:00 AM', '08:00 AM', '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '01:00 PM', '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM', '06:00 PM']
        self.dataframes = {}
        self.asig = asig_totales
        self.filas_aco = ['7', 0, '9', 0, '11', 0, 0, '2', 0, '4', 0]     

    def ListaDataframes(self):

        # Se crean todos los dataframes que serviran para visualizar graficamente los horarios. Esto se hace en función del numero de asignaturas y el número de grupos
        cantidad_horarios = list(set(map(lambda a: (a[1], a[-1]), self.asig))) 
        label_horarios = sorted(list(map( lambda x: f"NIVEL {x[0]} {self.grupos_letras[x[1]-1]}" , cantidad_horarios)))
        dataframes = dict(map( lambda x: (x , pd.DataFrame(np.nan, index=self.filas, columns=self.columnas)) , label_horarios))
        return dataframes
    
    def ConfiguracionVista(self):
        # Esto se hace para que el horario no se divida y no se muestre con normalidad
        pd.set_option('display.max_columns', None)
        pd.set_option('display.expand_frame_repr', False)

    def generarHorario(self, hof):
        
        self.ConfiguracionVista()
        dataframes = self.ListaDataframes()
        
        hof2_dividido = list(map(lambda x: (x[0], x[1:]), hof))
        def distribuir_datos(c,t): 
               if c[0] in self.asig_3h:  # Graficar asignaturas de 3 horas        
                dataframes[f"NIVEL {c[1]} {self.grupos_letras[c[-1]-1]}"].loc[self.filas[self.filas_aco.index(t[1])],  t[0]] = c[0]   
                dataframes[f"NIVEL {c[1]} {self.grupos_letras[c[-1]-1]}"].loc[self.filas[self.filas_aco.index(t[1])+1],t[0]] = c[0]
                dataframes[f"NIVEL {c[1]} {self.grupos_letras[c[-1]-1]}"].loc[self.filas[self.filas_aco.index(t[1])+2],t[0]] = c[0]   
               if c[2] == 2:             # Graficar asignaturas de 2 horas     
                dataframes[f"NIVEL {c[1]} {self.grupos_letras[c[-1]-1]}"].loc[self.filas[self.filas_aco.index(t[1])],  t[0]] = c[0]   
                dataframes[f"NIVEL {c[1]} {self.grupos_letras[c[-1]-1]}"].loc[self.filas[self.filas_aco.index(t[1])+1],t[0]] = c[0]
               else:                     # Graficar asignaturas de 1 hora
                dataframes[f"NIVEL {c[1]} {self.grupos_letras[c[-1]-1]}"].loc[self.filas[self.filas_aco.index(t[1])],  t[0]] = c[0]                        
        list(map(distribuir_datos , self.asig, hof2_dividido))
        return dataframes