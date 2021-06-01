__author__ = "Mathieu MOREL"
__copyright__ = "Copyright (C) 2021 Mathieu MOREL"
__license__ = "GPL"
__version__ = "1.5"
__maintainer__ = "Mathieu MOREL"
__email__ = "mathieu.morel@etu.emse.fr"
__status__ = "Test Stage"

import tkinter as tk
from tk import *
import tcl
from tkinter import ttk
import threading
from PIL import ImageTk, Image  
import tkinter.font as tkFont
from datetime import datetime
# Import
import sys
import os
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import functools
import subprocess

flag = 0x08000000  # No-Window flag
webdriver.common.service.subprocess.Popen = functools.partial(
    subprocess.Popen, creationflags=flag)

import time

import webbrowser # Pour ouvrir edge

import winsound # Pour faire le bip d'alerte
frequency = 1700  # Fréquence 1700 Hertz
duration = 700  # Durée 1000 ms == 1 seconde

import keyboard  # using module keyboard

from datetime import date # Pour comparer

browser = None
URL = None
choix_vaccin = None
mon_choix = None
nom_centre = None
OPTIONS = ('None', 'None', 'None')
buttonlaunch = None

# Class Path
type_vaccin_id      = "booking_motive"
age_id              = "booking_motive_category"
no_vaccin_xpath     = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div/div/div/div[1]/div/div/span"
button_pRDV_xpath = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/div/button/span" 
nom_centre_xpath    = "//*[@id='booking-content']/div[2]/div[1]/div/div[3]/div[1]/div"

# Vaccin Type
pfizer     = "1re injection vaccin COVID-19 (Pfizer-BioNTech)-5494"
pfizer2    = "2de injection vaccin COVID-19 (Pfizer-BioNTech)-5494"
moderna    = "1re injection vaccin COVID-19 (Moderna)-5494"
moderna2   = "2de injection vaccin COVID-19 (Moderna)-5494"

# Créneaux Xpath
days_xpath  = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div["
t_slots     = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/div[1]/div["
voirplus    = "//*[@id='booking-content']/div[2]/div[3]/div/div[2]/div[2]/div/div/div[1]/div/div/button/span"
premconsult = "//*[@id='booking-content']/div[2]/div[1]/div/div[3]/div[2]/div/label[2]/div"

# Faux Créneaux Class Name
faux_creneaux = "availabilities-empty-slot"

# Recherche si il y a possiblement un vaccin
def vaccin_dispo(id_choix):
    global browser
    global URL
    global choix_vaccin
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
    global browser
    try :
        browser.find_element_by_xpath(voirplus).click()
        time.sleep(0.2)
    except NoSuchElementException :
        return 0

#Uniquement si il y a ce widgets
def cliquer_premconsult():
    global browser
    try :
        browser.find_element_by_xpath(premconsult).click()
        time.sleep(0.2)
        return 2
    except NoSuchElementException :
        return 1

#Uniquement si il y a ce widgets age_id
def choix_age():
    global browser
    try :
        age_dropd = Select(browser.find_element_by_id(age_id))
        age_dropd.select_by_index(2)
        time.sleep(0.2)
        return 2
    except NoSuchElementException :
        return 1
    
# Affiche les créneaux
def afficher_creneaux():
    string_affichage = ""
    global browser
    global URL
    global choix_vaccin
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
            string_affichage += t_jour[index] +"\n"
            while test_heure:
                try :
                    creneaux_i = browser.find_element_by_xpath(t_slots[index]+str(heure_i)+"]")
                    string_affichage += creneaux_i.text  +"\n"
                    heure_i += 1
                    if creneaux_i.get_attribute("class") != faux_creneaux:
                        chronodosedispo += 1
                except NoSuchElementException :
                    test_heure = False
            heure_i = 1
            test_heure = True
        return chronodosedispo, string_affichage
    except NoSuchElementException :
        return 0, string_affichage
            
#Fonction qui regarde toutes les 3 secondes les disponibilités
def recherche_vaccins(id_choix):
    status = False # Pour éviter les sur-ouvertures dans le navigateur
    while not keyboard.is_pressed('q'):
        time.sleep(1)
        if vaccin_dispo(id_choix):
            if vaccin_dispo(id_choix): # Double check pour éviter les faux positifs
                chrono_doses = afficher_creneaux()[0]
                if chrono_doses != 0 :
                    winsound.Beep(frequency, duration) # Bip
                    if status == False :
                        print("Dépêchez-vous ! Des chronodoses semblent disponibles\n")
                        string_affichage = afficher_creneaux()[1]
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
    
    
# Connection
def connection():
    nom_centre = ""
    global browser
    global URL
    try:
        firefoxOptions = webdriver.FirefoxOptions()
        firefoxOptions.headless = True
        firefoxOptions.add_argument('--disable-gpu')
        
        #os.chdir(sys._MEIPASS)

        path = os.path.dirname(__file__)

        browser = webdriver.Firefox(executable_path=path+'\geckodriver.exe', options=firefoxOptions)

        browser.get(URL)
        time.sleep(0.5)
        choix_age()
        id_nom = cliquer_premconsult()
        nom_centre = browser.find_element_by_xpath("//*[@id='booking-content']/div[2]/div["+str(id_nom)+"]/div/div[3]/div[1]/div").text
        choix_age()
        return True, nom_centre
    except:
        return False, nom_centre

def dropdownvalues():
    global browser
    global URL
    global choix_vaccin
    time.sleep(0.2)
    choix_vaccin = Select(browser.find_element_by_id(type_vaccin_id))
            
    liste_choix = choix_vaccin.options
    liste_choix_str = ["1"+" - "+liste_choix[1].text]
    index = 0
    for choix in liste_choix :
        if index != 0:
            liste_choix_str.append(str(index)+" - "+choix.text)
        index+=1
    return liste_choix_str
    
def maintest():
    global mon_choix
    try:
        print("\n")
        print("Veuillez Patienter")
        print("Un son sera émis si une chronodose est disponible")
        print("Pour quitter, restez appuyé sur 'q'")
        recherche_vaccins(mon_choix)
    finally:
        try:
            browser.close()
        except:
            pass

LARGEFONT =("Verdana", 20)
  
class tkinterApp(tk.Tk):
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
         
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        
        # creating a container
        self.winfo_toplevel().title("MinuteDoses")
        path = os.path.dirname(__file__)
        self.iconbitmap(path+'\icon.ico')
        container = tk.Frame(self, width=500, height=650)
        container.pack_propagate(0)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_propagate(0)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # initializing frames to an empty array
        self.frames = {} 
  
        # iterating through a tuple consisting
        # of the different page layouts
        for F in (StartPage, HomePage, Page1, Page2):
  
            frame = F(container, self)
  
            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
            self.frames[F] = frame
  
            frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(StartPage)
  
    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
  
# first window frame startpage
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        path = os.path.dirname(__file__)
        bghome   = Image.open(path+"\\bghome.png")
        bghometk = ImageTk.PhotoImage(bghome)

        bghometklab = ttk.Label(self, image=bghometk)
        bghometklab.image = bghometk

        # Position image
        bghometklab.place(relx=0, rely=0)
  
        button1 = ttk.Button(self, text ="Commencer",
        command = lambda : controller.show_frame(HomePage))
     
        button1.place(relx=0.5, rely=0.90, anchor="center")  
        
  
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        
        path = os.path.dirname(__file__)
        bg1   = Image.open(path+"\\bg1.png")
        bg1tk = ImageTk.PhotoImage(bg1)

        bg1tklab = ttk.Label(self, image=bg1tk)
        bg1tklab.image = bg1tk

        # Position image
        bg1tklab.place(relx=0, rely=0)
  
        button1 = ttk.Button(self, text ="Commencer",
        command = lambda : controller.show_frame(Page1))
     
        # putting the button in its place by
        # using grid
        button1.place(relx=0.5, rely=0.90, anchor="center")  
        
# second window frame page1
class Page1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #background
        path = os.path.dirname(__file__)
        bg1   = Image.open(path+"\\bg2.png")
        bg1tk = ImageTk.PhotoImage(bg1)
        bg1tklab = ttk.Label(self, image=bg1tk)
        bg1tklab.image = bg1tk
        bg1tklab.place(relx=0, rely=0)

        
        entry1 = tk.Entry(self)
        
        def connect ():  
            global URL
            global nom_centre
            global OPTIONS
            URL = entry1.get()
            co_mess = ttk.Label(self, text ="Connection avec le centre en cours ...")
            co_mess.place(relx=0.5, rely=0.75, anchor="center")
            time.sleep(1)
            co_ok, nom_centre = connection()
            if co_ok :
                nom_centre_label = ttk.Label(self, text = nom_centre)
                nom_centre_label.place(relx=0.5, rely=0.75, anchor="center")
                OPTIONS = dropdownvalues()
                buttonrg = tk.Button(self, text='Choisir son vaccin', command=lambda:controller.show_frame(Page2))
                buttonrg.place(relx=0.5, rely=0.95, anchor="center")  
                
            else:
                co_mess = ttk.Label(self, text ="connection échouée, rééssayez !")
                co_mess.place(relx=0.5, rely=0.75, anchor="center")
        
        def start_connect_thread(event):
            global connect_thread
            connect_thread = threading.Thread(target=connect)
            connect_thread.daemon = True
            connect_thread.start()
            self.after(20, check_connect_thread)

        def check_connect_thread():
            if connect_thread.is_alive():
                self.after(20, check_connect_thread)
            
        
        entry1.place(relx=0.5, rely=0.65, anchor="center")
        
        boutonvaliderlien = tk.Button(self, text='Valider le lien', command=lambda:start_connect_thread(None))
        boutonvaliderlien.place(relx=0.5, rely=0.70, anchor="center")
  
  
  
  
class Page2(tk.Frame):
    global nom_centre
    global OPTIONS
    buttontest = None
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #background
        path = os.path.dirname(__file__)
        bg1   = Image.open(path+"\\bg3.png")
        bg1tk = ImageTk.PhotoImage(bg1)
        bg1tklab = ttk.Label(self, image=bg1tk)
        bg1tklab.image = bg1tk
        bg1tklab.place(relx=0, rely=0)
        self.bind("<<ShowFrame>>", self.on_show_frame)

    def on_show_frame(self, event):
        
        choix_possibles = tk.StringVar()
        choix_possibles.set("Veuillez choisir")
        dropdown = ttk.OptionMenu(self, choix_possibles, *OPTIONS)
        dropdown.place(relx=0.5, rely=0.36, anchor="center")
                
        def choix():
            global mon_choix
            global buttonlaunch
            mon_choix = int(choix_possibles.get()[0])
            nom_centre_label = ttk.Label(self, text = nom_centre)
            nom_centre_label.place(relx=0.5, rely=0.45, anchor="center")
            nom_vac_label = ttk.Label(self, text = choix_possibles.get())
            nom_vac_label.place(relx=0.5, rely=0.50, anchor="center")
            buttonlaunch = tk.Button(self, text='Commencer les recherches', command=lambda:start_rechercher_thread(None))
            buttonlaunch.place(relx=0.5, rely=0.70, anchor="center")
            
        def start_choix_thread(event):
            global choix_thread
            choix_thread = threading.Thread(target=choix)
            choix_thread.daemon = True
            choix_thread.start()
            self.after(20, check_choix_thread)

        def check_choix_thread():
            if choix_thread.is_alive():
                self.after(20, check_choix_thread)
                        
        buttonrg = tk.Button(self, text='Valider', command=lambda:start_choix_thread(None))
        buttonrg.place(relx=0.5, rely=0.4, anchor="center")
                
        def rechercher():
            global mon_choix
            global buttonlaunch
            buttonlaunch.grid_forget()
            
            textbox = tk.Text(self, width=60, height=12)
            textbox.place(relx=0.5, rely=0.80, anchor="center")
            textbox.tag_configure('center', justify='center')
            textbox.configure(font=('Segoe UI', 9))
            textbox.insert('0.0', "Début des recherches", 'center')
            
            status = False                    
            while True:
                time.sleep(1)
                if vaccin_dispo(mon_choix):
                    if vaccin_dispo(mon_choix): # Double check pour éviter les faux positifs
                        chrono_doses = afficher_creneaux()[0]
                        if chrono_doses != 0 :
                            winsound.Beep(frequency, duration) # Bip
                            if status == False :
                                now = datetime.now()
                                current_time = now.strftime("%H:%M:%S")
                                string_affichage = "Créneaux trouvés à "+current_time +"\nDépêchez-vous ! Des chronodoses semblent disponibles\n" + afficher_creneaux()[1]
                                webbrowser.open(URL) # Ouvre le nav. par défaut
                                status = True
                                
                                textbox.insert('1.0', string_affichage, 'center')
                                #cdisp = ttk.Label(self, text =string_affichage)
                                #cdisp.place(relx=0.5, rely=0.80, anchor="center")
                else:
                    #cdisp = ttk.Label(self, text ="Loose")
                    status = False

        def start_rechercher_thread(event):
            global choix_thread
            rechercher_thread = threading.Thread(target=rechercher)
            rechercher_thread.daemon = True
            rechercher_thread.start()
            self.after(20, check_rechercher_thread)

        def check_rechercher_thread():
            if choix_thread.is_alive():
                self.after(20, check_rechercher_thread)
  
  
# Driver Code
print("MinuteDoses par Mathieu MOREL")
print("Merci de ne pas fermer cette fenêtre")
app = tkinterApp()
app.mainloop()