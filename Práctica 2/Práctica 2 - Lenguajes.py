#Práctica 2 - Peñaflor Nicolás.

#Bloque 1 - Importaciones
import csv #para manejar archivos csv.
import json #para manejar archivos json.
from pathlib import Path #para manejar rutas de archivos y carpetas.
from datetime import datetime #para manejar fechas y tiempos.

#Bloque 2 - Variables
#Defino variables globales que voy a usar como constantes.
CARPETA_BASE = Path(__file__).parent 

ARCHIVO_ENTRADA = CARPETA_BASE / 'actividad_2.csv' 
CARPETA_SALIDA = CARPETA_BASE / 'salida' 

ARCHIVO_CSV_SALIDA = CARPETA_SALIDA / 'campeones.csv'
ARCHIVO_JSON_SALIDA = CARPETA_SALIDA / 'reporte.json'

DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']


#Bloque 3 - Procesamiento de datos.
def procesamiento(ruta_archivo):
    sesiones = [] #Creo una Lista vacía para guardar los datos.
    print(f"Leyendo archivo: {ruta_archivo}...")
    
    #Uso try/except para manejar errores de archivo.
    try:
        #Uso with open para abrir el archivo de forma segura.
        with open(ruta_archivo, 'r', encoding='utf-8') as f: 
            lector_csv = csv.DictReader(f) #Para leer cada fila como un Diccionario.
            
            #Hago un bucle for para recorrer cada fila, cada fila será un nuevo diccionario.
            for i, fila in enumerate(lector_csv, start=1):
                #Hago otro try/except para manejar posibles errores de fecha.
                try:
                    formato_fecha = "%Y-%m-%d %H:%M" #Defino una variable formato_fecha con el molde de fecha que utiliza nuestro archivo csv.
                    ts = datetime.strptime(fila['timestamp'], formato_fecha) #Convierto el texto o string en un objeto de datetime.
                    numero_dia = ts.weekday() #Obtengo el número del día de la semana (0=Lunes, 6=Domingo).
                    
                    actividad = fila['actividad'].lower()
                    if 'entrenamiento' in actividad:
                        #Le cargo al diccionario 'fila' los nuevos datos.
                        fila['timestamp_dt'] = ts
                        fila['dia_semana'] = numero_dia
                        fila['dia_semana_nombre'] = DIAS_SEMANA[numero_dia]
                    
                        #Agrego cada diccionario 'fila' a mi lista 'sesiones'.
                        sesiones.append(fila)
                        
                #Si 'strptime' falla, captura 'ValueError'.
                except ValueError:
                    print(f"Error: Timestamp inválido en línea {i}")
                #Si 'fila['timestamp']' falla, captura 'KeyError'.
                except KeyError:
                    print(f"Error: falta la columna timestamp en líne {i}")

    #Si 'with open' falla porque el archivo no existe.
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de entrada: {ruta_archivo}")
        return None
    #Si hay cualquier otro error inesperado.
    except Exception as e:
        print(f"Error inesperado al leer el archivo: {e}")
        return None
    
    #Verifico si la lista 'sesiones' está vacía.
    if not sesiones:
        print("No se leyeron datos válidos (o no se encontraron 'entrenamientos').")
        return None
        
    print(f"Se procesaron {len(sesiones)} sesiones DE ENTRENAMIENTO válidas.")
    return sesiones


# Bloque 4 - Análisis de datos.
def analisis(sesiones):
    
    #Creo un diccionario vacío para contar cuantas sesiones hubo cada día de la semana.
    conteo_por_dia = {}
    for dia in DIAS_SEMANA:
        conteo_por_dia[dia] = 0
            
    #Creo un diccionario para contar los campeones y otro para contar campeones en fines de semana.
    conteo_campeon = {}
    conteo_campeon_finde = {}
    
    #Creo el diccionario "externo" de un diccionario anidado.
    conteo_por_dia_y_por_campeon = {}
    #Acá voy a ir asignando los días como las keys de ese diccionario.
    for dia in DIAS_SEMANA:
        conteo_por_dia_y_por_campeon[dia] = {} 
    
    #Recorro cada sesión en la lista 'sesiones'.
    for sesion in sesiones:
        #Extraigo el nombre del día y del campeón para usarlos.
        dia_nombre = sesion['dia_semana_nombre']
        campeon = sesion['campeon']

        #Cuento la sesión por día.
        conteo_por_dia[dia_nombre] += 1
        
        #Cuento el campeón.
        if campeon in conteo_campeon:
            conteo_campeon[campeon] += 1
        else:
            conteo_campeon[campeon] = 1
                
        #Cuento el campeón (finde).
        if sesion['dia_semana'] >= 5: 
            if campeon in conteo_campeon_finde:
                conteo_campeon_finde[campeon] += 1
            else:
                conteo_campeon_finde[campeon] = 1
                    
        #Cuento cada campeón por cada día.
        #Ahora creo el diccionario interno del día actual.
        dic_interno_dia = conteo_por_dia_y_por_campeon[dia_nombre]
        
        if campeon in dic_interno_dia:
            dic_interno_dia[campeon] += 1
        else:
            dic_interno_dia[campeon] = 1
        
    # Devuelvo un diccionario que contiene todos los conteos.
    return {
        "conteo_por_dia": conteo_por_dia,
        "conteo_campeon": conteo_campeon, 
        "conteo_finde_campeon": conteo_campeon_finde, 
        "conteo_por_dia_y_por_campeon": conteo_por_dia_y_por_campeon 
    }

#Bloque 5 - Cálculos.
def calculos(sesiones, conteo_por_dia):

    #Por si no hay sesiones, retorno ceros en los promedios y None para el primer/último entrenamiento.
    if not sesiones:
        return {dia: 0 for dia in DIAS_SEMANA}, None, None
        
    sesiones_ordenadas = sorted(sesiones, key=lambda s: s['timestamp_dt']) #Con lambda le pido que ordene de acuerdo a la key 'timestamp_dt'. 
    primer_entrenamiento = sesiones_ordenadas[0]['timestamp_dt'].date()
    ultimo_entrenamiento = sesiones_ordenadas[-1]['timestamp_dt'].date()
    
    #Calculo el numero total de entrenamientos
    total_entrenamientos = sum(conteo_por_dia.values())
    
    #Creo un diccionario para guardar los promedios de cada día.
    promedios = {}
    for dia in DIAS_SEMANA:
        if total_entrenamientos > 0:
            promedios[dia] = (conteo_por_dia[dia] / total_entrenamientos) * 100
        else:
            promedios[dia] = 0
            
    return promedios, primer_entrenamiento, ultimo_entrenamiento


def maximos(recuento):

    #Medida de seguridad por si el diccionario que uso está vacío.
    if not recuento:
        return "Ninguno", 0
            
    #Busco el valor máximo en el diccionario.
    valor_maximo = 0
    for valor in recuento.values():
        if valor > valor_maximo:
            valor_maximo = valor
    
    #Busco todos los nombres que tienen ese valor máximo.
    nombres_maximos = []
    for nombre, valor in recuento.items():
        if valor == valor_maximo:
            nombres_maximos.append(nombre)
    
    #Retorno una cadena con los nombres separados por comas y el valor máximo.
    return ", ".join(nombres_maximos), valor_maximo


# Bloque 6 - Gneración de archivos.
#Csv con la cantidad de entrenamientos por campeón.
def generar_csv(conteo_campeon):
    try:
        CARPETA_SALIDA.mkdir(exist_ok=True)
        
        with open(ARCHIVO_CSV_SALIDA, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['campeon', 'cantidad'])

            for campeon, cantidad in conteo_campeon.items():
                writer.writerow([campeon, cantidad])
        print(f"Archivo CSV generado en {ARCHIVO_CSV_SALIDA}")
        
    except OSError as e:
        print(f"Error al escribir CSV en {ARCHIVO_CSV_SALIDA}: {e}")
            
#Json con el total de sesiones y el conteo por día y campeón.
def generar_json(total_sesiones, conteo_por_dia_y_por_campeon): 
    reporte = {
        'total_registros': total_sesiones,
        'entrenamientos_por_dia': conteo_por_dia_y_por_campeon
    }
    
    try:
        CARPETA_SALIDA.mkdir(exist_ok=True)
        
        with open(ARCHIVO_JSON_SALIDA, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)
        print(f"Archivo JSON generado en {ARCHIVO_JSON_SALIDA}")
        
    except OSError as e:
        print(f"Error al escribir JSON en {ARCHIVO_JSON_SALIDA}: {e}")


# Bloque 7 - Función Principl.
def main():
    
    print("Iniciando Práctica 2...")
    sesiones = procesamiento(ARCHIVO_ENTRADA)
    if not sesiones:
        print("Procesamiento detenido por error en la lectura.")
        return

    datos_analizados = analisis(sesiones)
    
    print("\nResultados")

    dia, sesiones_dia= maximos(datos_analizados["conteo_por_dia"])
    print(f"3. Día con más sesiones: {dia} ({sesiones_dia} sesiones)")

    promedios, primer_entrenamiento, ultimo_entrenamiento = calculos(sesiones, datos_analizados["conteo_por_dia"])
    
    if primer_entrenamiento and ultimo_entrenamiento:
        diferencia_dias = (ultimo_entrenamiento - primer_entrenamiento).days
        print(f"4. Días pasados entre el primer y último entrenamiento ({primer_entrenamiento} a {ultimo_entrenamiento}): {diferencia_dias} días")
    else:
        print("4. No se pudo calcular el rango de días (no se encontraron sesiones).")

    campeones, cantidad = maximos(datos_analizados["conteo_campeon"])
    print(f"5. Campeón que más entrenó: {campeones} (con {cantidad} sesiones)")


    print("6. Porcentaje de entrenamientos por día:")
    for dia, prom in promedios.items():
        total_dia = datos_analizados["conteo_por_dia"][dia]
        print(f"   - {dia:<10}: {prom:5.2f}% (Total: {total_dia})") 


    campeones_finde, cantidad_campeones_finde = maximos(datos_analizados["conteo_finde_campeon"])
    print(f"7. Campeón(es) que más entrena fines de semana: {campeones_finde} (con {cantidad_campeones_finde} sesiones)")

    print("\n Generando Archivos de Salida ")
    
    generar_csv(datos_analizados["conteo_campeon"])

    generar_json(len(sesiones), datos_analizados["conteo_por_dia_y_por_campeon"])
    
    print("\nProcesamiento completado.")


# Bloque 8 - Ejecución.
if __name__ == "__main__":
    main()