import numpy as np
import pandas as pd

# Anzahl der generierten Datensätze
num_samples = 9997 # plus 3 example services

# Liste der service namen
servie_names = ['Safety Tracker', 'Digital Manual', 'Movement Optimization']

# Liste der Hersteller
hersteller = ['Fraunhofer IPA', 
              'SOP', 
              'HAW']

# Liste der Funktionen der Services
functions = ['Ueberwachung', 
             'Analyse', 
             'Optimierung', 
             'Kommunikation', 
             'Assistenz',
             'Automatisierung',
             'Empfehlung',
             'Generierung',
             'Diagnose',
             'Sprachverarbeitung',
             'Clustering',
             'Mustererkennung']

# Generiere zufällige Trainingsdaten
data = {
    'Name': ['Service ' + str(i+1) for i in range(num_samples)],
    'Hersteller': np.random.choice(hersteller, size=num_samples),
    'Funktion': []
}

# loop through all elements and add functions - needs to be split in functions
for idx, type in enumerate(data['Name']):
    num = np.random.randint(low=1, high=4)
    selected_functions = np.random.choice(functions, size=num, replace=False)
    data['Funktion'].append(','.join(selected_functions))

# Erstelle DataFrame
df = pd.DataFrame(data)

# add 3 example services
new_row = {"Name": "Safety Tracker",
           "Hersteller": "Fraunhofer IPA",
           "Funktion": "Ueberwachung" }      
df.loc[len(df)] = new_row

new_row = {"Name": "Digital Manual",
           "Hersteller": "SOP",
           "Funktion": "Kommunikation, Assistenz" }      
df.loc[len(df)] = new_row

new_row = {"Name": "Movement Optimization",
           "Hersteller": "HAW",
           "Funktion": "Optimierung, Analyse" }      
df.loc[len(df)] = new_row

# Speichere Daten in einer CSV-Datei
df.to_csv('trainingsdaten_services_10000.csv', index=False)

# Name, Hersteller, Funktion
# Safety Tracker, Fraunhofer IPA, Ueberwachnug
# Digital Manual, SOP, "Kommunikation, Assistenz"
# Movement Optimization, HAW, "Optimierung, Analyse"

# --------------------------------------------------------------

# Generiere zufällige Trainingsdaten für Service-Maschinen-Interaktion
data_combi = {
    'Name_Service': ['Service ' + str(np.random.randint(low=1, high=10000) + (i*0)) for i in range(num_samples+3)],
    'Name_Maschine': ['Maschine ' + str(np.random.randint(low=1, high=10000) + (i*0)) for i in range(num_samples+3)],
    'AbsatzmengeFaktor': np.random.normal(loc=1.2, scale=0.1, size=num_samples+3),
    'PersonalkostenFaktor': np.random.normal(loc=0.9, scale=0.1, size=num_samples+3),
    'EnergiekostenFaktor': np.random.normal(loc=1, scale=0.02, size=num_samples+3),
    'ReparaturkostenProStueckFaktor': np.random.normal(loc=1, scale=0.02, size=num_samples+3),
    'MaterialkostenFaktor': np.random.normal(loc=1, scale=0.02, size=num_samples+3),
    'WartungskostenFaktor': np.random.normal(loc=1, scale=0.02, size=num_samples+3),
    'AbsatzpreisFaktor': np.random.normal(loc=1, scale=0.02, size=num_samples+3),
}

# Erstelle DataFrame
df_combi = pd.DataFrame(data_combi)

# Speichere Daten in einer CSV-Datei
df_combi.to_csv('trainingsdaten_kombination_10000.csv', index=False)