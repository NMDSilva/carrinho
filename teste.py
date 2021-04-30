import time
from datetime import datetime


inicial = datetime.now()
time.sleep(5)

final = datetime.now()
tempoSegundos = (final - inicial).total_seconds()
horas = divmod(tempoSegundos, 3600)
minutos = divmod(horas[1], 60)
segundos = divmod(minutos[1], 1)

print('Tempo de execução: %d horas, %d minutos e %d segundos' % (horas[0], minutos[0], segundos[0]))