__author__ = "Mathieu MOREL"
__copyright__ = "Copyright (C) 2021 Mathieu MOREL"
__license__ = "GPL"
__version__ = "1.3.6"
__maintainer__ = "Mathieu MOREL"
__email__ = "mathieu.morel@etu.emse.fr"
__status__ = "Test Stage"

# Import
import os
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.ui import Select

import time

import webbrowser # Pour ouvrir edge

import winsound # Pour faire le bip d'alerte
frequency = 1700  # Fréquence 1700 Hertz
duration = 700  # Durée 1000 ms == 1 seconde

import keyboard  # using module keyboard

from datetime import date # Pour comparer

# Docotolib URL
URL_dijon       = 'https://www.doctolib.fr/centre-de-sante/dijon/cpts-de-dijon-vaccination-covid-19-dijon?highlight%5Bspeciality_ids%5D%5B%5D=5494'
URL_parisdisney = 'https://www.doctolib.fr/centre-de-sante/seine-et-marne/grand-centre-de-vaccination-covid-19-disney-village?highlight%5Bspeciality_ids%5D%5B%5D=5494'
URL_obernai     = 'https://www.doctolib.fr/centre-de-sante/obernai/centre-de-vaccination-covid-gymnase-bugeaud-obernai?highlight%5Bspeciality_ids%5D%5B%5D=5494'
URL_marstest    = 'https://www.doctolib.fr/centre-de-sante/marseille/centre-de-vaccination-covid-cgd13-reserve-aux-professionnels-de-sante?highlight%5Bspeciality_ids%5D%5B%5D=5494'

URL_dev         = 'https://www.doctolib.fr/centre-de-sante/dijon/centre-de-sante-admr-dijon'

#URL = URL_dijon

# Class Path
type_vaccin_id      = "booking_motive"
no_vaccin_xpath     = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/span"
button_pRDV_xpath = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/div/button/span" 
nom_centre_xpath    = "//*[@id='booking-content']/div[2]/div[1]/div/div[3]/div[1]/div"

# Vaccin Type
pfizer     = "1re injection vaccin COVID-19 (Pfizer-BioNTech)-5494"
pfizer2    = "2de injection vaccin COVID-19 (Pfizer-BioNTech)-5494"
moderna    = "1re injection vaccin COVID-19 (Moderna)-5494"
moderna2   = "2de injection vaccin COVID-19 (Moderna)-5494"

test_choix = "Pansement-30"

choix = pfizer

# Créneaux Xpath
days_xpath  = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div["
t_slots     = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div["
voirplus    = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/button/span"
premconsult = "//*[@id='booking-content']/div[2]/div[1]/div/div[3]/div[2]/div/label[2]/div"

# Faux Créneaux Class Name
faux_creneaux = "availabilities-empty-slot"

# Recherche si il y a possiblement un vaccin
def vaccin_dispo(id_choix):
    choix_vaccin.select_by_index(0)
    time.sleep(0.5)
    choix_vaccin.select_by_index(id_choix)
    time.sleep(0.5)
    try:
        browser.find_element_by_xpath(no_vaccin_xpath)
    except NoSuchElementException:
        try:
            browser.find_element_by_xpath(button_pRDV_xpath)
        except NoSuchElementException:
            return True
        return False
    return False

#Uniquement si il y a beaucoup de créneaux
def cliquer_voir_plus():
    try :
        browser.find_element_by_xpath(voirplus).click()
        time.sleep(0.2)
        #print("bouton cliqué")
    except NoSuchElementException :
        #print("bouton non cliqué")
        return 0

#Uniquement si il y a beaucoup de créneaux
def cliquer_premconsult():
    try :
        browser.find_element_by_xpath(premconsult).click()
        time.sleep(0.2)
        #print("bouton cliqué")
        return 2
    except NoSuchElementException :
        #print("bouton non cliqué")
        return 1
    
# Affiche les créneaux
def afficher_creneaux(display):
    cliquer_voir_plus()
    today_day = str(date.today().day)
    try:
        test_jour = True
        j = 2
        id_jour = None
        while test_jour:
            day_i = browser.find_element_by_xpath(days_xpath+str(j)+"]/div[1]/div[2]").text
            if today_day in day_i:
                id_jour = j
                test_jour = False
            j += 1
        
        nb_jour = 2 # Nombre de jour à regarder | 2 pour chronodoses
        t_indexj = [id_jour + i for i in range(nb_jour)]
        t_jour   = ["Aujourd'hui :", "Demain :", "j+2", "j+3"] 
        t_slots  = [days_xpath + str(i) + "]/div[2]/div[" for i in t_indexj]
        
        test_heure = True
        heure_i = 1
        chronodosedispo = 0
        for index in range(len(t_indexj)):
            if display : print(t_jour[index])
            while test_heure:
                try :
                    creneaux_i = browser.find_element_by_xpath(t_slots[index]+str(heure_i)+"]")
                    if display : print(creneaux_i.text)
                    heure_i += 1
                    if creneaux_i.get_attribute("class") != faux_creneaux:
                        chronodosedispo += 1
                except NoSuchElementException :
                    test_heure = False
            heure_i = 1
            test_heure = True
        return chronodosedispo
    except NoSuchElementException :
        return 0
            
#Fonction qui regarde toutes les 3 secondes les disponibilités
def recherche_vaccins(id_choix):
    status = False # Pour éviter les sur-ouvertures dans le navigateur
    while not keyboard.is_pressed('q'):
        time.sleep(1)
        if vaccin_dispo(id_choix):
            if vaccin_dispo(id_choix): # Double check pour éviter les faux positifs
                chrono_doses = afficher_creneaux(False)
                if chrono_doses != 0 :
                    winsound.Beep(frequency, duration) # Bip
                    if status == False :
                        print("Dépêchez-vous ! Des chronodoses semblent disponibles\n")
                        afficher_creneaux(True)
                        webbrowser.open(URL) # Ouvre le nav. par défaut
                        status = True
        else :
            if status:
                print("Cette dose n'est désormais plus disponible")
                print("Veuillez à nouveau patienter")
                print("Un son sera émis si une chronodose est disponible")
                print("Pour quitter, restez appuyé sur 'q'")
            status = False
            
    print("Déconnection")
    
    
"""
DONE :
       Faire que le vaccin soit bien le lendemain ou jour même --> ok
       utiliser la fonction créneaux --> ok ;)
       !!! Il y avait un soucis avec le bouton voir +, en effet il
       est là uniquement en cas de nombreuses doses. -> fonction qui
       résout le pb -> ok
       pb affichage --> OK
       ERREUR -> variable chronodose incorrecte -> ok il fallait prendre
       en compte le nom de la classe avec getAttribute
 1.3.4 ajout du nom du centre  
 1.3.5 textes enrichis
       plus de duplicata pour un même affichage de créneaux
 1.3.6 mettre l'url en input -> ok
       automatiser le choix du vaccin -> ok
TODO :
       Mail ?
       Finir doctolib first --> URL marstest
       autre site ? 
"""


# Main
try:
    #print("Veuillez entrer votre URL :")
    #URL = input()
    
    URL = URL_dijon
    print("Connection..\n")
    firefoxOptions = webdriver.FirefoxOptions()
    firefoxOptions.headless = True
    path = os.path.dirname(__file__)
    browser = webdriver.Firefox(executable_path=path+'\geckodriver.exe', options=firefoxOptions)

    browser.get(URL)
    browser.page_source[:500]
    time.sleep(0.2)

    id_nom = cliquer_premconsult()
    nom_centre = browser.find_element_by_xpath("//*[@id='booking-content']/div[2]/div["+str(id_nom)+"]/div/div[3]/div[1]/div").text
    print("Connection avec le centre choisi établie :")
    print(nom_centre, "\n")
    
    choix_vaccin = Select(browser.find_element_by_id(type_vaccin_id))
    
    print("Les choix pour ce centre sont :")
    liste_choix = choix_vaccin.options
    index = 0
    for choix in liste_choix :
        if index != 0:
            print(str(index)+" - "+choix.text)
        index+=1
    print("Veuillez choisir votre vaccin en entrant le numéro correspondant :")
    id_choix = input()

    print("\n")
    print("Veuillez Patienter")
    print("Un son sera émis si une chronodose est disponible")
    print("Pour quitter, restez appuyé sur 'q'")
    
    recherche_vaccins(id_choix)
finally:
    try:
        browser.close()
    except:
        pass