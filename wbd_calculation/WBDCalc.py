from aas_client.AASClient import AASClient
import asyncio
import websockets
from omegaconf import OmegaConf
import numpy as np

# Maschine without AI
class CostsMaschineBase:
    
    # Fallbeispiel
    anschaffungskosten = 800000 # euro
    wiederbeschaffungskosten = 125000 # euro
    restlauferloes = 20000 # euro
    nutzdauerJahre = 10 # jahre
    zinssatz = 0.07
    kalkulatorischeAbschreibung = (wiederbeschaffungskosten - restlauferloes) / nutzdauerJahre #euro
    kalkulatorischerZins = ( ( anschaffungskosten + restlauferloes ) / 2 ) * zinssatz # euro
    fremdkapital = 100000 # euro

    # Für Kostenberechnung
    reparaturkostenProStueck = 0.03 # euro
    materialkostenStueck = 0.17 # euro
    energiekostenStueck = 0.09 # euro
    wartungskostenJahr = 3500 # euro
    personalkostenStueck = 0.13 # euro
    absatzmengeJahr = 500000
    absatzpreis = 0.51 # euro

    # Maschinennutzung
    maschinenlaufzeitJahr = 365 # tage
    maschinenlaufzeitProTag = 24 # stunden
    instandhaltungszeitImJahr = 50 # stunden
    raumbedarf = 50 # qubikmeter

    # Gewinn-/Kostenvergleichsrechnung
    personalkostenJahr = personalkostenStueck * absatzmengeJahr
    variableReparaturKostenImJahr = absatzmengeJahr * reparaturkostenProStueck
    instandhaltungskostenImJahr = wartungskostenJahr + variableReparaturKostenImJahr
    energiekostenJahr = energiekostenStueck * absatzmengeJahr
    materialkostenJahr = (materialkostenStueck * absatzmengeJahr)

    gesamtkosten = kalkulatorischeAbschreibung + kalkulatorischerZins + materialkostenJahr + energiekostenJahr + instandhaltungskostenImJahr + personalkostenJahr
    umsatzerloes = absatzmengeJahr * absatzpreis
    gewinnJahr = umsatzerloes - gesamtkosten

    def __init__(self):

        # get values from the AAS
        self.config = OmegaConf.load("client-config.yaml")
        self.aas_client = AASClient(self.config["aas"]["host"])
        values = self.aas_client.get_submodels()


    def calc(self):
        print()
        print("### - Gewinn Maschine Base - ###")
        print(self.kalkulatorischeAbschreibung)
        print(self.kalkulatorischerZins)
        print(self.materialkostenJahr)
        print(self.energiekostenJahr)
        print(self.instandhaltungskostenImJahr)
        print(self.personalkostenJahr)
        print()
        print("### - ###")
        print(self.gesamtkosten)
        print(self.umsatzerloes)
        print(self.gewinnJahr)

# Maschine with AI
class CostsAI:

    maschineBase: CostsMaschineBase
    maschineBase = CostsMaschineBase()

    # AI Factors
    absatzmengeFaktor = (1 + 0.06)
    personalkostenFaktor = (1 - 0.05)
    energiekostenFaktor = 1
    reparaturkostenProStueckFaktor = 1
    materialkostenFaktor = 1
    wartungskostenFaktor = 1
    absatzpreisFaktor = 1

    # Kosten inklusive KI Faktoren
    reparaturkostenProStueck = maschineBase.reparaturkostenProStueck * reparaturkostenProStueckFaktor # euro
    materialkostenStueck = maschineBase.materialkostenStueck * materialkostenFaktor # euro
    energiekostenStueck = maschineBase.energiekostenStueck * energiekostenFaktor # euro
    wartungskostenJahr = maschineBase.wartungskostenJahr * wartungskostenFaktor # euro
    personalkostenStueck = maschineBase.personalkostenStueck * personalkostenFaktor # euro
    absatzmengeJahr = maschineBase.absatzmengeJahr * absatzmengeFaktor
    absatzpreis = maschineBase.absatzpreis * absatzpreisFaktor # euro

    # Kosten KI
    beschaffungskostenProMaschine = 500 # euro
    anzahlMaschinen = 1
    trainingskosten = 10000 # euro
    arbeitszeitkostenEinrichtung = 900 # euro
    sonstigeKostenEinmalig = 0 # euro
    kiKostenImJahr = ( ( beschaffungskostenProMaschine * anzahlMaschinen ) + arbeitszeitkostenEinrichtung + trainingskosten + sonstigeKostenEinmalig ) / maschineBase.nutzdauerJahre

    # Gewinn-/Kostenvergleichsrechnung
    personalkostenJahr = personalkostenStueck * absatzmengeJahr
    variableReparaturKostenImJahr = absatzmengeJahr * reparaturkostenProStueck
    instandhaltungskostenImJahr = wartungskostenJahr + variableReparaturKostenImJahr
    energiekostenJahr = energiekostenStueck * absatzmengeJahr
    materialkostenJahr = (materialkostenStueck * absatzmengeJahr)
    
    gesamtkosten = maschineBase.kalkulatorischeAbschreibung + maschineBase.kalkulatorischerZins + materialkostenJahr + energiekostenJahr + instandhaltungskostenImJahr + personalkostenJahr + kiKostenImJahr
    umsatzerloes = absatzmengeJahr * absatzpreis
    gewinnJahr = umsatzerloes - gesamtkosten

    def __init__(self):
        # get values from the AAS
        self.config = OmegaConf.load("client-config.yaml")
        aas_client = AASClient(self.config["aas"]["host"])
        values = aas_client.get_submodels()     

    def calc(self):
        print()
        print("### - Gewinn Maschine With AI - ###")
        print(self.gesamtkosten)
        print(self.umsatzerloes)
        print(self.gewinnJahr)


# Kosten für den Maschinenbetreiber
class MaschineUser:

    arbeitsfreieTageImJahr = 115 # tage
    arbeitstageImJahr = 365 - arbeitsfreieTageImJahr # tage
    maschinenlaufzeitProTag = 24 # stunden
    arbeitsfreieStundenProTag = 8 # stunden
    arbeitsstundenProTag = 24 - arbeitsfreieStundenProTag
    betriebsbedingeStillstandzeitImJahr = 700 # stunden
    
    raumkostenProQubikmeter = 110 # euro
    energiebedarfProStunde = 200 # kWh
    energiekostensatzProQubikmeterProJahr = 0.1825 # euro

    def __init__(self):

        # get values from the AAS
        self.config = OmegaConf.load("client-config.yaml")
        aas_client = AASClient(self.config["aas"]["host"])
        values = aas_client.get_submodels()
