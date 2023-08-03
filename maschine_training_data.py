import numpy as np
import pandas as pd

# Anzahl der generierten Datensätze
num_samples = 9997 # + 3 for example machines

# Liste der Maschinentypen
machine_names = ['Trumpf TruLaser 1030 fiber', 'DMG MORI DMP 70', 'Heidelberg Speedmaster CX 104']

# Liste der Maschinentypen
machine_types = ['Laserschneidmaschine', 
                 'CNC-Fräse', 
                 'Druckmaschine', 
                 'Roboterarm', 
                 'FTS', 
                 'Drehmaschine', 
                 'Schleifmaschine', 
                 'Spritzgussmaschine', 
                 'Presse', 
                 'Verpackungsmaschine', 
                 'Wasserstrahlschneidmaschine',
                 '3D-Drucker',
                 'Lackiermaschine']

# Liste der Werkstoffe
materials = ['Metall', 
             'Holz', 
             'Kunststoff', 
             'Gummi', 
             'Verbundwekstoff',
             'Textil',
             'Papier',
             'Glas',
             'Keramik',
             'Stein',
             'Beton']

# Liste der Bearbeitungsarten
operations = ['Fräsen', 
              'Drehen', 
              'Bohren', 
              'Stanzen',
              'Schweißen',
              'Schneiden',
              'Pressen',
              'Drucken',
              '3D-Drucken',
              'Schleifen',
              'Biegen',
              'Lackieren',
              'Transportieren',
              'Giessen']

# Liste der Werkzeuge
tools =      ['Laser', 
              'Bohrer', 
              'Walzfräser', 
              'Prismenfräser',
              'Wasserstrahl',
              'Wolframelektrode',
              'Elektrode',
              'Greifer',
              'Tintenstrahl',
              'Messer',
              'Lackierpistole',
              'Schleifpapier',
              'Heizelement',
              'Duese',
              'Foerderband']

# Liste erlaubter Materialien (anhängig vom Maschinentyp)
allowed_materials  = {'Laserschneidmaschine' : ['Metall', 'Holz', 'Kunststoff', 'Verbundwerkstoff', 'Glas', 'Stein'], 
                      'CNC-Fräse' : ['Metall', 'Holz', 'Kunststoff', 'Stein'], 
                      'Druckmaschine' : ['Holz', 'Papier', 'Keramik', 'Textil'], 
                      'Roboterarm' : ['Metall', 'Holz', 'Kunststoff', 'Verbundwerkstoff', 'Glas', 'Stein', 'Gummi', 'Textil', 'Papier', 'Keramik', 'Beton'], 
                      'FTS' : ['Metall', 'Holz', 'Kunststoff', 'Verbundwerkstoff', 'Glas', 'Stein', 'Gummi', 'Textil', 'Papier', 'Keramik', 'Beton'], 
                      'Drehmaschine' : ['Metall', 'Holz', 'Kunststoff', 'Stein'], 
                      'Schleifmaschine' : ['Metall', 'Holz', 'Kunststoff', 'Stein'], 
                      'Spritzgussmaschine' : ['Metall'], 
                      'Presse' : ['Metall', 'Holz', 'Kunststoff'], 
                      'Verpackungsmaschine' : ['Papier', 'Kunststoff'], 
                      'Wasserstrahlschneidmaschine' : ['Metall', 'Holz', 'Kunststoff', 'Verbundwerkstoff', 'Glas', 'Stein', 'Keramik', 'Beton'],
                      '3D-Drucker' : ['Metall', 'Kunststoff'],
                      'Lackiermaschine' : ['Metall', 'Holz', 'Kunststoff', 'Verbundwerkstoff', 'Glas', 'Stein']}

# Liste erlaubter Bearbeitungsarten (anhängig vom Maschinentyp)
allowed_operations = {'Laserschneidmaschine' : ['Fräsen', 'Bohren', 'Schneiden', 'Stanzen'], 
                      'CNC-Fräse' : ['Fräsen', 'Drehen', 'Drehen', 'Schneiden', 'Schleifen'], 
                      'Druckmaschine' : ['Drucken', 'Lackieren'], 
                      'Roboterarm' : ['Transportieren', 'Fräsen', 'Drehen', 'Bohren', 'Schweißen', 'Schneiden', '3D-Drucken', 'Schleifen', 'Biegen', 'Lackieren'], 
                      'FTS' : ['Transportieren'], 
                      'Drehmaschine' : ['Drehen'], 
                      'Schleifmaschine' : ['Schleifen'], 
                      'Spritzgussmaschine' : ['Giessen'], 
                      'Presse' : ['Pressen', 'Stanzen'], 
                      'Verpackungsmaschine' : ['Biegen', 'Transportieren'], 
                      'Wasserstrahlschneidmaschine' : ['Schneiden'],
                      '3D-Drucker' : ['3D-Drucken'],
                      'Lackiermaschine' : ['Lackieren']}

# Liste erlaubter Werkzeuge (abhängig vom Maschinentyp)
allowed_tools = {'Laserschneidmaschine' : ['Laser', 'Heizelement'], 
                 'CNC-Fräse' : ['Bohrer', 'Walzfräser', 'Prismenfräser'], 
                 'Druckmaschine' : ['Tintenstrahl', 'Laser', 'Lackierpistole', 'Heizelement'], 
                 'Roboterarm' : ['Greifer', 'Bohrer', 'Wasserstrahl', 'Wolframelektrode', 'Elektrode', 'Lackierpistole', 'Messer', "Schleifpapier"], 
                 'FTS' : ['Greifer'], 
                 'Drehmaschine' : ['Bohrer', 'Messer', 'Walzfräser', 'Prismenfräser'], 
                 'Schleifmaschine' : ['Schleifpapier'], 
                 'Spritzgussmaschine' : ['Duese'], 
                 'Presse' : ['Messer'], 
                 'Verpackungsmaschine' : ['Foerderband'], 
                 'Wasserstrahlschneidmaschine' : ['Wasserstrahl'],
                 '3D-Drucker' : ['Duese', 'Greifer'],
                 'Lackiermaschine' : ['Lackierpistole']}

# Generiere zufällige Trainingsdaten
data = {
    'Name': ['Maschine ' + str(i+1) for i in range(num_samples)],
    'Typ': np.random.choice(machine_types, size=num_samples),
    'DurchsatzProStunde': np.random.randint(low=10, high=10001, size=num_samples),
    'Werkstoff': [],
    'Werkzeuge': [],
    'Bearbeitungsart': []
}

# loop through all elements and add operations, material and tools - needs to be split in functions
for idx, type in enumerate(data['Typ']):
    choose_operations = allowed_operations[type]
    max_num = 1
    if (len(choose_operations) >= 3):
      max_num = 3
    else:
      max_num = 1
    num = np.random.randint(low=1, high=max_num+1)
    selected_operations = np.random.choice(choose_operations, size=num, replace=False)
    data['Bearbeitungsart'].append(','.join(selected_operations))
    choose_tools = allowed_tools[type]
    if (len(choose_tools) >= 3):
      max_num = 3
    else:
      max_num = 1
    num = np.random.randint(low=1, high=max_num+1)
    selected_tools = np.random.choice(choose_tools, size=num, replace=False)
    data['Werkzeuge'].append(','.join(selected_tools))
    choose_materials = allowed_materials[type]
    if (len(choose_materials) >= 3):
      max_num = 3
    else:
      max_num = 1
    num = np.random.randint(low=1, high=max_num+1)
    selected_materials = np.random.choice(choose_materials, size=num, replace=False)
    data['Werkstoff'].append(','.join(selected_materials))

# Erstelle DataFrame
df = pd.DataFrame(data)

# add 3 example machines
new_row = {"Name": "Trumpf TruLaser 1030 fiber",
           "Typ": "Laserschneidmaschine",
           "DurchsatzProStunde": 1000,
           "Werkstoff": "Metall",
           "Werkzeuge": "Laser",
           "Bearbeitungsart": "Schneiden"}      
df.loc[len(df)] = new_row

new_row = {"Name": "DMG MORI DMP 70",
           "Typ": "CNC-Fräse",
           "DurchsatzProStunde": 200,
           "Werkstoff": "Metall",
           "Werkzeuge": "Walzenfräser, Prismenfräser",
           "Bearbeitungsart": "Fräsen"}      
df.loc[len(df)] = new_row

new_row = {"Name": "Heidelberg Speedmaster CX 104",
           "Typ": "Druckmaschine",
           "DurchsatzProStunde": 20000,
           "Werkstoff": "Papier",
           "Werkzeuge": "Laser",
           "Bearbeitungsart": "Drucken"}      
df.loc[len(df)] = new_row

# Speichere Daten in einer CSV-Datei
df.to_csv('trainingsdaten_maschinen_10000.csv', index=False)

# Example machines
# Name,Typ,DurchsatzProStunde,Werkstoff,Werkzeuge,Bearbeitungsart
# Trumpf TruLaser 1030 fiber, Laserschneidmaschine, 1000, Metall, Laser, Schneiden
# DMG MORI DMP 70,CNC-Fräse, 200, Metall, "Walzenfräser,Prismenfräser", Fräsen
# Heidelberg Speedmaster CX 104, Druckmaschine, 20000, Papier, Laser, Drucken