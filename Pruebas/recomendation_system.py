from surprise import Dataset
from surprise import Reader
from surprise.model_selection import train_test_split
from surprise import KNNBasic
from surprise import KNNWithMeans
from surprise import KNNWithZScore
from surprise import accuracy
from surprise.model_selection import cross_validate
from surprise.model_selection import KFold
from collections import defaultdict
import operator

def get_top_n(predictions, user, n=10):
  def filter_by_user(entry):
    return entry[0] == user
  
  iterator = filter(filter_by_user, predictions)
  filtered_list = list(iterator)
  top_n = {}
  # Then sort the predictions for each user and retrieve the k highest ones.
  for uid, iid, true_r, est, _ in filtered_list:
    top_n[iid] = est
  result = sorted(top_n.items(), key=operator.itemgetter(1))
  return result[:n]

file_path = './games_100_summary.csv'
# Formato del dataset. Elemento separador. Rating mínimo y máximo.
reader = Reader(line_format='user item rating', sep=',', rating_scale=(1, 10))
data = Dataset.load_from_file(file_path, reader=reader)
# Preparación de los datos. 2 aproximaciones
# Primera aproximación - Creación de un conjunto de prueba y otro de entrenamiento.

# trainSet, testSet = train_test_split(data, test_size=0.2)

# Segunda aproximación - Usar todos los datos existentes para la creación del sistema
# Se optará por este
trainSet = data.build_full_trainset()
# Utilización de algoritmos kNN (Vecindades) Se considerará filtrado colaborativo
# Consideraciones importantes
#   - k es un valor customizable. Implica la cantidad de items a considerar para estimar las recomendaciones
#   - Se puede asignar en su lugar un valor mínimo para k. Si un usuario no alcanza el mínimo, se usará la media global
#   - Existe otro parámetro, que es la "similaridad". Se trata de una serie de opciones que permiten al algoritmo detectar
#     que items son similares a otros. Se trata de un diccionario.
#       - user_based: Si True, busca usuarios similares. Si False, busca similitudes entre items.
#       - min_support: La cantidad mínima de puntos comunes. Básicamente, cuántos usuarios como mínimo tienen que haber puntuado lo mismo.
#       - name: Nombre de la fórmula interna usuada para calcular la similiritud. Ninguna opción es necesariamente mejor que otras.
#         - cosine
#         - MSD
#         - pearson
# En Surprise, existen 4 algoritmos kNN. Estos determinan como un usuario U valoraría un item I.
#   - KNNBasic: Promedio de las calificaciones del usuario ponderado por las similiritudes.
#   - KNNWithMeans: Similar a la anterior pero más ajustada al consdiderar el promedio de las calificaciones de los items.
#   - KNNWithZScore: Un ajuste todavía mayor al considerar la desviación estándar de las calificaciones.
# CONSIDERACIONES: El primero es el menos útil, especilamente si los items tienen todos medias diferentes.
k = 15
minimunK = 5
options = {
  'name': 'pearson',
  'user_based': False,
}

# algo = KNNBasic(k = k, min_k = minimunK, sim_option = options)
algo = KNNWithMeans(k = k, min_k = minimunK, sim_option = options)
# algo = KNNWithZScore(k = k, min_k = minimunK, sim_option = options)
algo.fit(trainSet)

# Si queremos visualizar la matrix de similiritud
# algo.sim
# Formato numpy. Puede ser útil para hacer predicciones manuale
# Testeo del sistema entrenado. Existen 4 métricas disponibles
# - RMSE -> Este es el estándar que se usa profesionalmente a día de hoy
# - FCP 
# - MAE
# - MSE 
# CONSIDERACIONES: Si se quiere hacer validación cruzada, se debe trabajar con el dataset completo en el entrenamiento.

# Ejemplo sin validación cruzada.
# predictions = algo.test(testset)
# accuracy.rmse(predictions) # La puntuación que se obtiene es la desviación media.

# Para hacer validación cruzada, hace falta utilizar el método cross_validate. Parámetros:
# - cv: Se especifica el iterador que se desea utilizar. Esto va a afectar a la manera en la que se seleccionan valores
#   para el entrenamiento y la prueba. Documentación:https://surprise.readthedocs.io/en/stable/model_selection.html?highlight=cross%20validation#module-surprise.model_selection.split
# - n_jobs: La cantidad de entradas que se van a evaluar en paralelo. -1 implica la máxima posible. Puede llevar a crasheos.
# - algo: Algoritmo a usar. El anteriomente creado. Es importante tener en cuenta, que el algoritmo se entrena con el dataset que se haya usado como parámetro en el método fit().
# - data: Dataset original con todos los datos.
# - measures: Array con los nombres de los métodos de validación a usar.
# - return_train_measures: Parámetro booleano. Si es verdadero, la función devolverá datos del proceso.

results = cross_validate( # Tarda en finalizar. Se ejecuta unas 3 veces por cv=3
    algo = algo, data = data, measures=['RMSE'], 
    cv=2, return_train_measures=True
    )
print(results['test_rmse'].mean())

# Hay una alternativa al código anterior:
# kf = KFold(n_splits=3)
# for trainset, testset in kf.split(data):
#     algo.fit(trainset)
#     predictions = algo.test(testset)
#     accuracy.rmse(predictions, verbose=True)

# PREDICCIONES - CONSIDERACIONES
#  - Las predicciones se usuarios solo se pueden hacer en usuarios que se encuentren en el Datase

predictResult = algo.predict(uid = 'DRCrain', iid = '174430') # Hacemos una predicción y con los IDs reales. UID es el user id. iid es el item id
# Se obtiene una tupla. De esta, la clave 'est' contiene el valor de la predicción. 'r_ui' es valor real de existir si no, None.
print (predictResult)
# Obtención de los K vecinos (usuarios parecidos)
userRid = trainSet.to_inner_uid('DRCrain')
vecinos = algo.get_neighbors(userRid, k=10)
for x in vecinos: 
  print(trainSet.to_raw_uid(x))

# Para obtener las k recomendaciones, lo mejor es crear un anti set. Esto es un set con todos los items que el usuario no valoró, y su estimación en puntuación.
# Las predicciones las haríamos pues, con este segundo conjunto.
setForKItems = trainSet.build_anti_testset()
recomendations = algo.test(setForKItems)
top_n = get_top_n(recomendations, 'DRCrain', n=10)
print (top_n)