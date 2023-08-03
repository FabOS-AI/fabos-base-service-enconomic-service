from aas_client.AASClient import AASClient
import asyncio
import websockets
from omegaconf import OmegaConf
import numpy as np

# Maschine without AI
class CostsMaschineBase:

    # Fallbeispiel
    anschaffungskosten = 0 # euro
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

    def init_submodel(self):

        # get values from the AAS
        self.config = OmegaConf.load("client-config.yaml")
        self.aas_client = AASClient(self.config["aas"]["host"])
        submodel = self.aas_client.get_maschine_submodel()
        self.submodelElements = submodel["submodelElements"]
        self.load_values()

    def load_values(self):    
        # Loop through each object in the submodel elements
        for element in self.submodelElements:
            # Check if the object's name matches the name we're looking for
            if element["idShort"] == "Anschaffungskosten":
                self.anschaffungskosten = element["value"]
            elif element["idShort"] == "Wiederbeschaffungskosten":
                self.wiederbeschaffungskosten = element["value"]
            elif element["idShort"] == "Restlauferloes":
                self.restlauferloes = element["value"]
            elif element["idShort"] == "NutzdauerJahre":
                self.nutzdauerJahre = element["value"]
            elif element["idShort"] == "Zinssatz":
                self.zinssatz = element["value"]
            elif element["idShort"] == "KalkulatorischeAbschreibung":
                self.kalkulatorischeAbschreibung = element["value"]
            elif element["idShort"] == "KalkulatorischerZins":
                self.kalkulatorischerZins = element["value"]
            elif element["idShort"] == "Fremdkapital":
                self.fremdkapital = element["value"]
            elif element["idShort"] == "ReparaturkostenProStueck":
                self.reparaturkostenProStueck = element["value"]
            elif element["idShort"] == "MaterialkostenStueck":
                self.materialkostenStueck = element["value"]
            elif element["idShort"] == "EnergiekostenStueck":
                self.energiekostenStueck = element["value"]
            elif element["idShort"] == "WartungskostenJahr":
                self.wartungskostenJahr = element["value"]
            elif element["idShort"] == "PersonalkostenStueck":
                self.personalkostenStueck = element["value"]
            elif element["idShort"] == "AbsatzmengeJahr":
                self.absatzmengeJahr = element["value"]
            elif element["idShort"] == "Absatzpreis":
                self.absatzpreis = element["value"]
            elif element["idShort"] == "MaschinenlaufzeitJahr":
                self.maschinenlaufzeitJahr = element["value"]
            elif element["idShort"] == "MaschinenlaufzeitProTag":
                self.maschinenlaufzeitProTag = element["value"]
            elif element["idShort"] == "InstandhaltungszeitImJahr":
                self.instandhaltungszeitImJahr = element["value"]
            elif element["idShort"] == "Raumbedarf":
                self.raumbedarf = element["value"]
            elif element["idShort"] == "PersonalkostenJahr":
                self.personalkostenJahr = element["value"]
            elif element["idShort"] == "VariableReparaturkostenImJahr":
                self.variableReparaturKostenImJahr = element["value"]
            elif element["idShort"] == "InstandhaltungskostenImJahr":
                self.instandhaltungskostenImJahr = element["value"]
            elif element["idShort"] == "EnergiekostenJahr":
                self.energiekostenJahr = element["value"]
            elif element["idShort"] == "MaterialkostenJahr":
                self.materialkostenJahr = element["value"]
            elif element["idShort"] == "Gesamtkosten":
                self.gesamtkosten = element["value"]
            elif element["idShort"] == "Umsatzerloes":
                self.umsatzerloes = element["value"]
            elif element["idShort"] == "GewinnJahr":
                self.gewinnJahr = element["value"]
            else: 
                print("not Found - " + element["idShort"])

    def calc(self):

        self.load_values()

        # set calc values in aas
        self.kalkulatorischeAbschreibung = (float(self.wiederbeschaffungskosten) - float(self.restlauferloes)) / float(self.nutzdauerJahre) #euro
        self.kalkulatorischerZins = ( ( float(self.anschaffungskosten) + float(self.restlauferloes) ) / 2 ) * float(self.zinssatz) # euro

        # Gewinn-/Kostenvergleichsrechnung
        self.personalkostenJahr = float(self.personalkostenStueck) * float(self.absatzmengeJahr)
        self.variableReparaturKostenImJahr = float(self.absatzmengeJahr) * float(self.reparaturkostenProStueck)
        self.instandhaltungskostenImJahr = float(self.wartungskostenJahr) + float(self.variableReparaturKostenImJahr)
        self.energiekostenJahr = float(self.energiekostenStueck) * float(self.absatzmengeJahr)
        self.materialkostenJahr = float(self.materialkostenStueck) * float(self.absatzmengeJahr)

        self.gesamtkosten = (
            float(self.kalkulatorischeAbschreibung)
            + float(self.kalkulatorischerZins)
            + float(self.materialkostenJahr)
            + float(self.energiekostenJahr)
            + float(self.instandhaltungskostenImJahr)
            + float(self.personalkostenJahr)
        )
        self.umsatzerloes = float(self.absatzmengeJahr) * float(self.absatzpreis)
        self.gewinnJahr = self.umsatzerloes - self.gesamtkosten

        # send values to aas server
        self.aas_client.set_value("WBDMaschineSubmodel", "KalkulatorischeAbschreibung", str(self.kalkulatorischeAbschreibung))
        self.aas_client.set_value("WBDMaschineSubmodel", "KalkulatorischerZins", str(self.kalkulatorischerZins))
        self.aas_client.set_value("WBDMaschineSubmodel", "PersonalkostenJahr", str(self.personalkostenJahr))
        self.aas_client.set_value("WBDMaschineSubmodel", "VariableReparaturkostenImJahr", str(self.variableReparaturKostenImJahr))
        self.aas_client.set_value("WBDMaschineSubmodel", "InstandhaltungskostenImJahr", str(self.instandhaltungskostenImJahr))
        self.aas_client.set_value("WBDMaschineSubmodel", "EnergiekostenJahr", str(self.energiekostenJahr))
        self.aas_client.set_value("WBDMaschineSubmodel", "MaterialkostenJahr", str(self.materialkostenJahr))
        self.aas_client.set_value("WBDMaschineSubmodel", "Gesamtkosten", str(self.gesamtkosten))
        self.aas_client.set_value("WBDMaschineSubmodel", "Umsatzerloes", str(self.umsatzerloes))
        self.aas_client.set_value("WBDMaschineSubmodel", "GewinnJahr", str(self.gewinnJahr))

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

    def init_submodel(self):
        # get values from the AAS
        self.config = OmegaConf.load("client-config.yaml")
        self.aas_client = AASClient(self.config["aas"]["host"])
        submodel = self.aas_client.get_ai_submodel()
        submodelMaschine = self.aas_client.get_maschine_submodel()
        self.submodelElements = submodel["submodelElements"] 
        self.submodelMaschineElements = submodelMaschine["submodelElements"] 
        self.load_values()

    def load_values(self):
        # Loop through each object in the AI submodel elements
        for element in self.submodelElements:
            # Check if the object's name matches the name we're looking for
            if element["idShort"] == "Anschaffungskosten":
                self.anschaffungskosten = element["value"]
            elif element["idShort"] == "Wiederbeschaffungskosten":
                self.wiederbeschaffungskosten = element["value"]
            elif element["idShort"] == "AbsatzmengeFaktor":
                self.absatzmengeFaktor = element["value"]
            elif element["idShort"] == "PersonalkostenFaktor":
                self.personalkostenFaktor = element["value"]
            elif element["idShort"] == "EnergiekostenFaktor":
                self.energiekostenFaktor = element["value"]
            elif element["idShort"] == "ReparaturkostenProStueckFaktor":
                self.reparaturkostenProStueckFaktor = element["value"]
            elif element["idShort"] == "MaterialkostenFaktor":
                self.materialkostenFaktor = element["value"]
            elif element["idShort"] == "WartungskostenFaktor":
                self.wartungskostenFaktor = element["value"]
            elif element["idShort"] == "AbsatzpreisFaktor":
                self.absatzpreisFaktor = element["value"]
            elif element["idShort"] == "ReparaturkostenProStueck":
                self.reparaturkostenProStueck = element["value"]
            elif element["idShort"] == "MaterialkostenStueck":
                self.materialkostenStueck = element["value"]
            elif element["idShort"] == "EnergiekostenStueck":
                self.energiekostenStueck = element["value"]
            elif element["idShort"] == "WartungskostenJahr":
                self.wartungskostenJahr = element["value"]
            elif element["idShort"] == "PersonalkostenStueck":
                self.personalkostenStueck = element["value"]
            elif element["idShort"] == "AbsatzmengeJahr":
                self.absatzmengeJahr = element["value"]
            elif element["idShort"] == "Absatzpreis":
                self.absatzpreis = element["value"]
            elif element["idShort"] == "BeschaffungskostenProMaschine":
                self.beschaffungskostenProMaschine = element["value"]
            elif element["idShort"] == "AnzahlMaschinen":
                self.anzahlMaschinen = element["value"]
            elif element["idShort"] == "Trainingskosten":
                self.trainingskosten = element["value"]
            elif element["idShort"] == "ArbeitszeitkostenEinrichtung":
                self.arbeitszeitkostenEinrichtung = element["value"]
            elif element["idShort"] == "SonstigeKostenEinmalig":
                self.sonstigeKostenEinmalig = element["value"]
            elif element["idShort"] == "KiKostenImJahr":
                self.kiKostenImJahr = element["value"]
            elif element["idShort"] == "PersonalkostenJahr":
                self.personalkostenJahr = element["value"]
            elif element["idShort"] == "VariableReparaturkostenImJahr":
                self.variableReparaturKostenImJahr = element["value"]
            elif element["idShort"] == "InstandhaltungskostenImJahr":
                self.instandhaltungskostenImJahr = element["value"]
            elif element["idShort"] == "EnergiekostenJahr":
                self.energiekostenJahr = element["value"]
            elif element["idShort"] == "MaterialkostenJahr":
                self.materialkostenJahr = element["value"]
            elif element["idShort"] == "Gesamtkosten":
                self.gesamtkosten = element["value"]
            elif element["idShort"] == "Umsatzerloes":
                self.umsatzerloes = element["value"]
            elif element["idShort"] == "GewinnJahr":
                self.gewinnJahr = element["value"]
            else: 
                print("not Found - " + element["idShort"])
        
        # Loop through each object in the Maschine submodel elements
        for element in self.submodelMaschineElements:
            # Check if the object's name matches the name we're looking for
            if element["idShort"] == "Anschaffungskosten":
                self.maschineBase.anschaffungskosten = element["value"]
            elif element["idShort"] == "Wiederbeschaffungskosten":
                self.maschineBase.wiederbeschaffungskosten = element["value"]
            elif element["idShort"] == "Restlauferloes":
                self.maschineBase.restlauferloes = element["value"]
            elif element["idShort"] == "NutzdauerJahre":
                self.maschineBase.nutzdauerJahre = element["value"]
            elif element["idShort"] == "Zinssatz":
                self.maschineBase.zinssatz = element["value"]
            elif element["idShort"] == "KalkulatorischeAbschreibung":
                self.maschineBase.kalkulatorischeAbschreibung = element["value"]
            elif element["idShort"] == "KalkulatorischerZins":
                self.maschineBase.kalkulatorischerZins = element["value"]
            elif element["idShort"] == "Fremdkapital":
                self.maschineBase.fremdkapital = element["value"]
            elif element["idShort"] == "ReparaturkostenProStueck":
                self.maschineBase.reparaturkostenProStueck = element["value"]
            elif element["idShort"] == "MaterialkostenStueck":
                self.maschineBase.materialkostenStueck = element["value"]
            elif element["idShort"] == "EnergiekostenStueck":
                self.maschineBase.energiekostenStueck = element["value"]
            elif element["idShort"] == "WartungskostenJahr":
                self.maschineBase.wartungskostenJahr = element["value"]
            elif element["idShort"] == "PersonalkostenStueck":
                self.maschineBase.personalkostenStueck = element["value"]
            elif element["idShort"] == "AbsatzmengeJahr":
                self.maschineBase.absatzmengeJahr = element["value"]
            elif element["idShort"] == "Absatzpreis":
                self.maschineBase.absatzpreis = element["value"]
            elif element["idShort"] == "MaschinenlaufzeitJahr":
                self.maschineBase.maschinenlaufzeitJahr = element["value"]
            elif element["idShort"] == "MaschinenlaufzeitProTag":
                self.maschineBase.maschinenlaufzeitProTag = element["value"]
            elif element["idShort"] == "InstandhaltungszeitImJahr":
                self.maschineBase.instandhaltungszeitImJahr = element["value"]
            elif element["idShort"] == "Raumbedarf":
                self.maschineBase.raumbedarf = element["value"]
            elif element["idShort"] == "PersonalkostenJahr":
                self.maschineBase.personalkostenJahr = element["value"]
            elif element["idShort"] == "VariableReparaturkostenImJahr":
                self.maschineBase.variableReparaturKostenImJahr = element["value"]
            elif element["idShort"] == "InstandhaltungskostenImJahr":
                self.maschineBase.instandhaltungskostenImJahr = element["value"]
            elif element["idShort"] == "EnergiekostenJahr":
                self.maschineBase.energiekostenJahr = element["value"]
            elif element["idShort"] == "MaterialkostenJahr":
                self.maschineBase.materialkostenJahr = element["value"]
            else: 
                print("not Found - " + element["idShort"])

    def calc(self):

        self.load_values()

        # set calc values in aas
        self.maschineBase.kalkulatorischeAbschreibung = (float(self.maschineBase.wiederbeschaffungskosten) - float(self.maschineBase.restlauferloes)) / float(self.maschineBase.nutzdauerJahre) #euro
        self.maschineBase.kalkulatorischerZins = ( ( float(self.maschineBase.anschaffungskosten) + float(self.maschineBase.restlauferloes) ) / 2 ) * float(self.maschineBase.zinssatz) # euro

        print ("-----")
        print(float(self.maschineBase.anschaffungskosten))
        print(float(self.maschineBase.restlauferloes))
        print(float(self.maschineBase.zinssatz))
        print("----")
        self.kalkulatorischerZins = ( ( float(self.maschineBase.anschaffungskosten) + float(self.maschineBase.restlauferloes) ) / 2 ) * float(self.maschineBase.zinssatz) # euro
        # Kosten inklusive KI Faktoren
        self.reparaturkostenProStueck = float(self.maschineBase.reparaturkostenProStueck) * float(self.reparaturkostenProStueckFaktor) # euro
        self.materialkostenStueck = float(self.maschineBase.materialkostenStueck) * float(self.materialkostenFaktor) # euro
        self.energiekostenStueck = float(self.maschineBase.energiekostenStueck) * float(self.energiekostenFaktor) # euro
        self.wartungskostenJahr = float(self.maschineBase.wartungskostenJahr) * float(self.wartungskostenFaktor) # euro
        self.personalkostenStueck = float(self.maschineBase.personalkostenStueck) * float(self.personalkostenFaktor) # euro
        self.absatzmengeJahr = float(self.maschineBase.absatzmengeJahr) * float(self.absatzmengeFaktor)
        self.absatzpreis = float(self.maschineBase.absatzpreis) * float(self.absatzpreisFaktor) # euro

        # Gewinn-/Kostenvergleichsrechnung
        self.personalkostenJahr = float(self.personalkostenStueck) * float(self.absatzmengeJahr)
        self.variableReparaturKostenImJahr = float(self.absatzmengeJahr) * float(self.reparaturkostenProStueck)
        self.instandhaltungskostenImJahr = float(self.wartungskostenJahr) + float(self.variableReparaturKostenImJahr)
        self.energiekostenJahr = float(self.energiekostenStueck) * float(self.absatzmengeJahr)
        self.materialkostenJahr = float(self.materialkostenStueck) * float(self.absatzmengeJahr)
        self.kiKostenImJahr = ( ( float(self.beschaffungskostenProMaschine) * float(self.anzahlMaschinen) ) + float(self.arbeitszeitkostenEinrichtung) + float(self.trainingskosten) + float(self.sonstigeKostenEinmalig) ) / float(self.maschineBase.nutzdauerJahre)

        self.gesamtkosten = (
            float(self.maschineBase.kalkulatorischeAbschreibung)
            + float(self.maschineBase.kalkulatorischerZins)
            + float(self.materialkostenJahr)
            + float(self.energiekostenJahr)
            + float(self.instandhaltungskostenImJahr)
            + float(self.personalkostenJahr)
            + float(self.kiKostenImJahr)
        )
        self.umsatzerloes = float(self.absatzmengeJahr) * float(self.absatzpreis)
        self.gewinnJahr = self.umsatzerloes - self.gesamtkosten

        # send values to aas server
        self.aas_client.set_value("WBDAISubmodel", "ReparaturkostenProStueck", str(self.reparaturkostenProStueck))
        self.aas_client.set_value("WBDAISubmodel", "MaterialkostenStueck", str(self.materialkostenStueck))
        self.aas_client.set_value("WBDAISubmodel", "EnergiekostenStueck", str(self.energiekostenStueck))
        self.aas_client.set_value("WBDAISubmodel", "WartungskostenJahr", str(self.wartungskostenJahr))
        self.aas_client.set_value("WBDAISubmodel", "PersonalkostenStueck", str(self.personalkostenStueck))
        self.aas_client.set_value("WBDAISubmodel", "AbsatzmengeJahr", str(self.absatzmengeJahr))
        self.aas_client.set_value("WBDAISubmodel", "Absatzpreis", str(self.absatzpreis))
        self.aas_client.set_value("WBDAISubmodel", "PersonalkostenJahr", str(self.personalkostenJahr))
        self.aas_client.set_value("WBDAISubmodel", "VariableReparaturkostenImJahr", str(self.variableReparaturKostenImJahr))
        self.aas_client.set_value("WBDAISubmodel", "InstandhaltungskostenImJahr", str(self.instandhaltungskostenImJahr))
        self.aas_client.set_value("WBDAISubmodel", "EnergiekostenJahr", str(self.energiekostenJahr))
        self.aas_client.set_value("WBDAISubmodel", "MaterialkostenJahr", str(self.materialkostenJahr))
        self.aas_client.set_value("WBDAISubmodel", "Gesamtkosten", str(self.gesamtkosten))
        self.aas_client.set_value("WBDAISubmodel", "Umsatzerloes", str(self.umsatzerloes))
        self.aas_client.set_value("WBDAISubmodel", "GewinnJahr", str(self.gewinnJahr))

        print()

        print("### - Gewinn Maschine Base - ###")
        print(self.maschineBase.kalkulatorischeAbschreibung)
        print(self.maschineBase.kalkulatorischerZins)
        print(self.materialkostenJahr)
        print(self.energiekostenJahr)
        print(self.instandhaltungskostenImJahr)
        print(self.personalkostenJahr)
        print(self.kiKostenImJahr)
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

    def init_submodel(self):
        # get values from the AAS
        self.config = OmegaConf.load("client-config.yaml")
        aas_client = AASClient(self.config["aas"]["host"])
        submodel = aas_client.get_maschine_user_submodel()
        submodelElements = submodel["submodelElements"] 

        # Loop through each object in the submodel elements
        for element in submodelElements:
            # Check if the object's name matches the name we're looking for
            if element["idShort"] == "ArbeitsfreieTageImJahr":
                self.arbeitsfreieTageImJahr = element["value"]
            elif element["idShort"] == "ArbeitstageImJahr":
                self.arbeitstageImJahr = element["value"]
            elif element["idShort"] == "MaschinenlaufzeitProTag":
                self.maschinenlaufzeitProTag = element["value"]
            elif element["idShort"] == "ArbeitsfreieStundenProTag":
                self.arbeitsfreieStundenProTag = element["value"]
            elif element["idShort"] == "ArbeitsstundenProTag":
                self.arbeitsstundenProTag = element["value"]
            elif element["idShort"] == "BetriebsbedingeStillstandzeitImJahr":
                self.betriebsbedingeStillstandzeitImJahr = element["value"]
            elif element["idShort"] == "RaumkostenProQubikmeter":
                self.raumkostenProQubikmeter = element["value"]
            elif element["idShort"] == "EnergiebedarfProStunde":
                self.energiebedarfProStunde = element["value"]
            elif element["idShort"] == "EnergiekostensatzProQubikmeterProJahr":
                self.energiekostensatzProQubikmeterProJahr = element["value"]
