#! pyhton3
# dati covid-19 italia
# 1) Mappa interattiva Italia (dashboard)
# http://www.salute.gov.it/portale/nuovocoronavirus/dettaglioContenutiNuovoCoronavirus.jsp?area=nuovoCoronavirus&id=5351&lingua=italiano&menu=vuoto
#
# 2) Github:  Dati dei contagi
#   https://github.com/pcm-dpc/COVID-19/blob/master/dati-json/dpc-covid19-ita-andamento-nazionale.json

import requests
import fake_useragent
import json
import pprint
import matplotlib.pyplot as plt
import os
import time
import datetime
from statsmodels.tsa.ar_model import AutoReg

# Andamento nazionale dei casi in Italia
url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-andamento-nazionale.json'
# Aggiornamento ultimo giorno
url_latest = 'https://github.com/pcm-dpc/COVID-19/blob/master/dati-json/dpc-covid19-ita-andamento-nazionale-latest.json'

ua = fake_useragent.UserAgent(verify_ssl=False)
res = requests.get(url, {"User-Agent": ua.random})
res.raise_for_status()

ita_dati = json.loads(res.text)


class Dati():
    def __init__(self):
        self.giorni = []
        self.data = []
        self.totale_positivi = []
        self.nuovi_positivi = []
        self.variazione_totale_positivi = []
        self.dimessi_guariti = []
        self.deceduti = []
        self.totale_casi = []
        self.terapia_intensiva = []
        self.totale_ospedalizzati = []
        self.tamponi = []
        self.tamponi_per_giorno = [0.001]
        self.rapporto_nuovi_contagi_casi_testati = []
        self.delta_deceduti = [0]


def store_ita_data(store, data_source):
    for i in (range(len(data_source))):
        store.giorni.append(i)
        store.data.append(data_source[i]['data'][:10])
        store.totale_positivi.append(data_source[i]['totale_positivi'])
        store.nuovi_positivi.append(data_source[i]['nuovi_positivi'])
        store.variazione_totale_positivi.append(data_source[i]['variazione_totale_positivi'])
        store.dimessi_guariti.append(data_source[i]['dimessi_guariti'])
        store.deceduti.append(data_source[i]['deceduti'])
        store.totale_casi.append(data_source[i]['totale_casi'])
        store.terapia_intensiva.append((data_source[i]['terapia_intensiva']))
        store.totale_ospedalizzati.append(data_source[i]['totale_ospedalizzati'])
        store.tamponi.append(data_source[i]['tamponi'])
        if i + 1 < len(data_source):
            store.tamponi_per_giorno.append(data_source[i + 1]['tamponi'] - data_source[i]['tamponi'])
            store.delta_deceduti.append(data_source[i + 1]['deceduti'] - data_source[i]['deceduti'])
        store.rapporto_nuovi_contagi_casi_testati.append(
            float("{:.2f}".format(100 * store.variazione_totale_positivi[i]
                                  / store.tamponi_per_giorno[i])))


dati_italia = Dati()
store_ita_data(dati_italia, ita_dati)

periodo = f"{ita_dati[0]['data'][:10]} - {ita_dati[-1]['data'][:10]}"

print(f"\nDati relativi a {len(ita_dati)} giorni del periodo: {periodo}")

print(f'\nPercentuale nuovi positivi su tamponi:\n{dati_italia.rapporto_nuovi_contagi_casi_testati}')

print(f'\nTotale Deceduti per giorno:\n {dati_italia.delta_deceduti}')

print(f'\nTerapia intensiva:\n {dati_italia.terapia_intensiva}')

print(f'\nTotale ospedalizzati:\n {dati_italia.totale_ospedalizzati}')

print('\nDati ultimo giorno:')
pprint.pprint(ita_dati[-1])

fig_nr = 1


def plot(store, data_to_plot):
    global fig_nr
    plt.figure(fig_nr)
    plt.plot(store.giorni, data_to_plot)
    plt.yscale("log")
    plt.title(f"periodo: {periodo}")
    plt.xlabel('giorni')
    plt.ylabel('')
    plt.show()
    fig_nr += 1


def plot_all(store):
    plot(store, store.nuovi_positivi)
    plot(store, store.rapporto_nuovi_contagi_casi_testati)
    plot(store, store.delta_deceduti)
    plot(store, store.totale_ospedalizzati)
    plot(store, store.terapia_intensiva)


def plot_log(store):
    global fig_nr
    plt.figure(fig_nr)
    plt.plot(store.giorni, store.totale_positivi, label='totale positivi')
    plt.annotate(str(store.totale_positivi[-1]), xy=(store.giorni[-1], store.totale_positivi[-1]))
    plt.plot(store.giorni, store.totale_ospedalizzati, label='ospedalizzati')
    plt.annotate(str(store.totale_ospedalizzati[-1]), xy=(store.giorni[-1], store.totale_ospedalizzati[-1]))
    plt.plot(store.giorni, store.terapia_intensiva, label='terapia intensiva')
    plt.annotate(str(store.terapia_intensiva[-1]), xy=(store.giorni[-1], store.terapia_intensiva[-1]))
    plt.plot(store.giorni, store.delta_deceduti, label='deceduti')
    plt.annotate(str(store.delta_deceduti[-1]), xy=(store.giorni[-1], store.delta_deceduti[-1]))
    plt.yscale("log")
    plt.title(f"periodo: {periodo}")
    plt.xlabel('giorni')
    plt.xlabel('log')
    plt.ylabel('')
    plt.legend()
    plt_title = 'situazione_giorno_'+str(store.giorni[-1])
    plt.savefig('Pictures/'+plt_title+'.png')
    plt.show()
    fig_nr += 1


# plot_all(dati_italia)
plot_log(dati_italia)


def autoregression(store):
    # AR example
    # https://machinelearningmastery.com/time-series-forecasting-methods-in-python-cheat-sheet/
    giorni_passati = 3 * 7  # giorni passati usati per fare le previsioni
    giorni_futuri = 2 * 7  # giorni futuri su cui si estende la previsione
    # contrived dataset
    data = store.totale_positivi[len(store.totale_positivi) - giorni_passati:]
    # fit model
    model = AutoReg(data, lags=1)
    model_fit = model.fit()
    # make prediction
    giorni = store.giorni[len(store.giorni) - giorni_passati:] + \
             [store.giorni[-1] + i for i in range(1, giorni_futuri + 1)]
    # https://www.statsmodels.org/stable/generated/statsmodels.tsa.ar_model.AR.predict.html
    yhat = list(map(int, model_fit.predict(start=0, end=len(data) + giorni_futuri, dynamic=False)))
    print(f"giorni: {len(giorni)} yhat: {len(yhat)}")
    return giorni, yhat


def plot_forecast(store):
    # chiama la funzione per ricavare i dati da plottare
    giorni, yhat = autoregression(store)
    global fig_nr
    plt.figure(fig_nr)
    plt.plot(store.giorni, store.totale_positivi, label='totale positivi')
    plt.annotate(str(store.totale_positivi[-1]), xy=(store.giorni[-1], store.totale_positivi[-1]))
    plt.plot(giorni, yhat, label='autoregressione')
    plt.annotate(str(yhat[-1]), xy=(giorni[-1], yhat[-1]))
    plt.yscale("log")
    plt.title(f"periodo: {periodo} \n Previsione 14 giorni")
    plt.xlabel('giorni')
    plt.ylabel('')
    plt.legend()
    plt_title = 'previsions_giorno_'+str(store.giorni[-1])
    plt.savefig('Pictures/'+plt_title+'.png')
    plt.show()
    fig_nr += 1


def write_to_log_file(store):
    # definisce il nome del file di log
    log_file_name = 'covid_19.log'
    # chiama la funzione che fa la previsione del totale positivi
    _, yhat = autoregression(store)

    def today():
        return datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

    def write_title():
        f.write(f"{'data corrente':<30}"
                f"{'totale positivi':<30}"
                f"{'nuovi positivi':<30}"
                f"{'totale ospedalizzati':<30}"
                f"{'terapia intensiva':<30}"
                f"{'delta deceduti':<30}"
                f"{'previsioni 14 giorni (totali positivi)':<30}")

    def write_content():
        f.write(f"{today():<30}"
                f"{store.totale_positivi[-1]:<30}"
                f"{store.variazione_totale_positivi[-1]:<30}"
                f"{store.totale_ospedalizzati[-1]:<30}"
                f"{store.terapia_intensiva[-1]:<30}"
                f"{store.delta_deceduti[-1]:<30}"
                f"{yhat[-1]:<30}")

    with open(log_file_name, 'a') as f:
        # se il file non è ancora stato creato scrive i titoli delle colonne ed i contenuti
        if os.stat(log_file_name).st_size == 0:
            write_title()
            f.write("\n")

        print(time.ctime(os.stat(log_file_name).st_mtime))
        write_content()
        f.write("\n")


plot_forecast(dati_italia)
write_to_log_file(dati_italia)

# # ********************************************************************************
# # Dati regionali
# # ********************************************************************************
#
# url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni-latest.json'
# ua = fake_useragent.UserAgent(verify_ssl=False)
# res = requests.get(url, {"User-Agent": ua.random})
# res.raise_for_status()
# regioni_dati_latest = json.loads(res.text)
# len(regioni_dati_latest)  # 21
#
# url = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-regioni.json'
# ua = fake_useragent.UserAgent(verify_ssl=False)
# res = requests.get(url, {"User-Agent": ua.random})
# res.raise_for_status()
# regioni_dati = json.loads(res.text)
# len(regioni_dati)
#
# denominazione_regione_dict = {
#     "Abruzzo": 0,
#     "Basilicata": 1,
#     "Calabria": 2,
#     "Campania": 3,
#     "Emilia-Romagna": 4,
#     "Friuli Venezia Giulia": 5,
#     "Lazio": 6,
#     "Liguria": 7,
#     "Lombardia": 8,
#     "Mrche": 9,
#     "Molise": 10,
#     "P.A. Bolzano": 11,
#     "P.A. Trento": 12,
#     "Piemonte": 13,
#     "Puglia": 14,
#     "Sardegna": 15,
#     "Sicilia": 16,
#     "Toscana": 17,
#     "Umbria": 18,
#     "Valle d'Aosta": 19,
#     "Veneto": 20,
# }
#
#
# def get_regional_data(nome_regione):
#     """
#     ottiene i dati di una singola regione
#     :param nome_regione: stringa con il nome delle regione (vedi denominazione_regioni_dict)
#     :param store: istanza della classe Dati
#     :return: lista dei dati
#     """
#     numero_regioni = 21
#     numero_dati = int(len(regioni_dati) / numero_regioni)
#     for i in range(numero_dati):
#         indice_regione = denominazione_regione_dict[nome_regione] + numero_regioni * i
#         print(regioni_dati[indice_regione]['denominazione_regione'])
#         print(regioni_dati[indice_regione]['totale_ospedalizzati'])
#
#
# def avoid_zero_elem(x):
#     """Per eliminare il problema della divisione per zero"""
#     if x == 0:
#         return 0.001
#     return x
#
# def store_regional_data(store, data_source, nome_regione):
#     numero_regioni = 21
#     # per ciascuna regione:
#     numero_dati = int(len(data_source) / numero_regioni)
#     for i in range(numero_dati):
#         # calcolo degli indici della regione che si vuole considerare
#         indice_regioner = denominazione_regione_dict[nome_regione] + numero_regioni * i
#         assert data_source[indice_regioner]['denominazione_regione'] == nome_regione, "Nome regione non corretto"
#         store.giorni.append(indice_regioner)
#         store.data.append(data_source[indice_regioner]['data'][:10])
#         store.totale_positivi.append(data_source[indice_regioner]['totale_positivi'])
#         store.nuovi_positivi.append(data_source[indice_regioner]['nuovi_positivi'])
#         store.variazione_totale_positivi.append(data_source[indice_regioner]['variazione_totale_positivi'])
#         store.dimessi_guariti.append(data_source[indice_regioner]['dimessi_guariti'])
#         store.deceduti.append(data_source[indice_regioner]['deceduti'])
#         store.totale_casi.append(data_source[indice_regioner]['totale_casi'])
#         store.terapia_intensiva.append((data_source[indice_regioner]['terapia_intensiva']))
#         store.totale_ospedalizzati.append(data_source[indice_regioner]['totale_ospedalizzati'])
#         store.tamponi.append(data_source[indice_regioner]['tamponi'])
#     for i in range(len(store.giorni)-1):
#         store.tamponi_per_giorno.append(store.tamponi[i + 1] - store.tamponi[i])
#         store.tamponi_per_giorno = list(map(avoid_zero_elem, store.tamponi_per_giorno))
#         store.delta_deceduti.append(store.deceduti[i + 1] - store.deceduti[i])
#         store.rapporto_nuovi_contagi_casi_testati.append(
#             float("{:.2f}".format(100 * store.variazione_totale_positivi[i]
#                                   / store.tamponi_per_giorno[i])))
#
#
# # get_regional_data('Puglia')
#
#
# dati_puglia = Dati()
# store_regional_data(dati_puglia, regioni_dati, 'Puglia')
#
# print(f'\nPuglia, totale ospedalizzati:\n {dati_puglia.totale_ospedalizzati}')
# print(f'\nPuglia, terapia intensiva:\n {dati_puglia.terapia_intensiva}')
# print(f'\nPuglia, tamponi:\n {dati_puglia.tamponi}')
# print(f'\nPuglia, tamponi per giorno:\n {dati_puglia.tamponi_per_giorno}')
# print(f'\nPuglia, variazione totale positivi:\n {dati_puglia.variazione_totale_positivi}')
# print(f'\nPuglia, rapporto nuovi contagi:\n {dati_puglia.rapporto_nuovi_contagi_casi_testati}')
