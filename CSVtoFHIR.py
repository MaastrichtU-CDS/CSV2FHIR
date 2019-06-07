import os
import io
import sys
import csv
import logging
from datetime import datetime
from collections import OrderedDict
import jinja2
from flask import Flask, render_template
import requests

this = os.getcwd()
keys = ['pat_id', 'gender', 'birthDate', 'deceasedBoolean', 'stage', 'ecog', 'ecogText', 'smok_stat', 'smok-statText','fev1', "bmi", 'tumorload', 'tnmstage', 'tnmstage_text', "Hist", "Hist_Text", "overallstage", "overallstagedisp", "bodycode", "bodydisp"]
fhirDict = OrderedDict().fromkeys(keys, None)

def populate_Data(data, fhirDict):
    # Get Patient Information
    fhirDict['pat_id'] = 'Maastro' + data['study_id']
    if data['gender'] == '1':
        fhirDict['gender'] = 'male'
    elif data['gender'] == '2':
        fhirDict['gender'] = 'female'
    else:
        fhirDict['gender'] = 'Unknown'
    fhirDict['birthDate'] = year = datetime.now().year - int(float(data['age']))
    if data['deadstat'] == '1':
        fhirDict['deceasedBoolean'] = 'true'
    else:
        fhirDict['deceasedBoolean'] = 'false'

    # Observation - ECOG Performance Status
    if data['who3g'] == '0':
        fhirDict['ecog'] = '425389002'
        fhirDict['ecogText'] = 'Ecog Performance Status 0'
    elif data['who3g'] == '1':
        fhirDict['ecog'] = '422512005'
        fhirDict['ecogText'] = 'Ecog Performance Status 1'
    elif data['who3g'] == '2':
        fhirDict['ecog'] = '422894000'
        fhirDict['ecogText'] = 'Ecog Performance Status 2'
    elif data['who3g'] == '3':
        fhirDict['ecog'] = '423053003'
        fhirDict['ecogText'] = 'Ecog Performance Status 3'
    elif data['who3g'] == '4':
        fhirDict['ecog'] = '423237006'
        fhirDict['ecogText'] = 'Ecog Performance Status 4'
    elif data['who3g'] == '5':
        fhirDict['ecog'] = '423409001'
        fhirDict['ecogText'] = 'Ecog Performance Status 5'
    else:
        fhirDict['ecog'] = '261665006'
        fhirDict["ecogText"] = "Unknown"
    # Observation - Smoking Status
    if data['dumsmok2'] == '1':
        fhirDict['smok_stat'] = '446172000'
        fhirDict['smok-statText']="Never/ex smoker"
    if data['dumsmok2'] == '2':
        fhirDict['smok_stat'] = '8392000'
        fhirDict['smok-statText'] = "Current Smoker"
    else:
        fhirDict['smok_stat'] = '261665006'
        fhirDict['smok-statText'] = "Unknown"
    # Observation - BMI
    fhirDict['bmi'] = data['bmi']
    # FEV1
    fhirDict['fev1'] = data['fev1pc_t0']
    # gtv1
    fhirDict["tumorload"] = data['gtv1']
    # Histology - observation
    if data["hist4g"] == "1":
        fhirDict["Hist"] = "8070/3"
        fhirDict["Hist_Text"] = "Squamous Cell Carcinoma"
    elif data["hist4g"] == "2":
        fhirDict["Hist"] = "8140/3"
        fhirDict["Hist_Text"] = "Adenocarcinoma"
    elif data["hist4g"] == "3":
        fhirDict["Hist"] = "8012/3"
        fhirDict["Hist_Text"] = "Large Cell Carcinoma"
    elif data["hist4g"] == "4":
        fhirDict["Hist"] = "other"
        fhirDict["Hist_Text"] = "Other"
    elif data["hist4g"] == "0":
        fhirDict["Hist"] = "261665006"
        fhirDict["Hist_Text"] = "Unknown"
    else:
        fhirDict["Hist"] = "385432009"
        fhirDict["Hist_Text"] = "Not Applicable"
    # tstage - observation
    if data["tstage"] == "1":
        fhirDict["tnmstage"] = "23351008"
        fhirDict["tnmstage_text"] = "T0/T1"
    elif data["tstage"] == "2":
        fhirDict["tnmstage"] = "67673008"
        fhirDict["tnmstage_text"] = "T2"
    elif data["tstage"] == "3":
        fhirDict["tnmstage"] = "14410001"
        fhirDict["tnmstage_text"] = "T3"
    elif data["tstage"] == "4":
        fhirDict["tnmstage"] = "65565005"
        fhirDict["tnmstage_text"] = "T4"
    elif data["tstage"] == "5":
        fhirDict["tnmstage"] = "67101007"
        fhirDict["tnmstage_text"] = "TX"
    elif data["tstage"] == "9":
        fhirDict["tnmstage"] = "missing"
        fhirDict["tnmstage_text"] = "Missing"
    elif data["tstage"] == "99":
        fhirDict["tnmstage"] = "261665006"
        fhirDict["tnmstage_text"] = "Unknown"
    else:
        fhirDict["tnmstage"] = "385432009"
        fhirDict["tnmstage_text"] = "Not Applicable"
    # Nstage observation
    if data["nstage"] == "1":
        fhirDict["tnmstage"] = "62455006"
        fhirDict["tnmstage_text"] = "N0"
    elif data["nstage"] == "2":
        fhirDict["tnmstage"] = "53623008"
        fhirDict["tnmstage_text"] = "N1"
    elif data["nstage"] == "3":
        fhirDict["tnmstage"] = "46059003"
        fhirDict["tnmstage_text"] = "N2"
    elif data["nstage"] == "4":
        fhirDict["tnmstage"] = "5856006"
        fhirDict["tnmstage_text"] = "N3"
    elif data["nstage"] == "5":
        fhirDict["tnmstage"] = "79420006"
        fhirDict["tnmstage_text"] = "NX"
    elif data["nstage"] == "99":
        fhirDict["tnmstage"] = "261665006"
        fhirDict["tnmstage_text"] = "Unknown"
    else:
        fhirDict["tnmstage"] = "385432009"
        fhirDict["tnmstage_text"] = "Not Applicable"
    # Condition Lung Cancer
    # bodysite
    if data["t_ct_loc"] == "1":
        fhirDict["bodycode"] = "266005"
        fhirDict["bodydisp"] = "Right lower lobe of lung"
    elif data["t_ct_loc"] == "2":
        fhirDict["bodycode"] = "72481006"
        fhirDict["bodydisp"] = "Right middle lobe of lung"
    elif data["t_ct_loc"] == "3":
        fhirDict["bodycode"] = "not available"
        fhirDict["bodydisp"] = "Right Hilus"
    elif data["t_ct_loc"] == "4":
        fhirDict["bodycode"] = "42400003"
        fhirDict["bodydisp"] = "Right upper lobe of lung"
    elif data["t_ct_loc"] == "5":
        fhirDict["bodycode"] = "41224006"
        fhirDict["bodydisp"] = "Left lower lobe of lung"
    elif data["t_ct_loc"] == "6":
        fhirDict["bodycode"] = "44714003"
        fhirDict["bodydisp"] = "left upper lobe"
    elif data["t_ct_loc"] == "7":
        fhirDict["bodycode"] = "not available"
        fhirDict["bodydisp"] = "Left Hilus"
    elif data["t_ct_loc"] == "8":
        fhirDict["bodycode"] = "72410000"
        fhirDict["bodydisp"] = "mediastinum"
    elif data["t_ct_loc"] == "9":
        fhirDict["bodycode"] = "385432009"
        fhirDict["bodydisp"] = "not applicable"
    elif data["t_ct_loc"] == "10":
        fhirDict["bodycode"] = "50837003"
        fhirDict["bodydisp"] = "Structure of Lingula of Left Lung"
    elif data["t_ct_loc"] == "11":
        fhirDict["bodycode"] = "45653009"
        fhirDict["bodydisp"] = "Upper lobe of lung"
    elif data["t_ct_loc"] == "12":
        fhirDict["bodycode"] = "90572001"
        fhirDict["bodydisp"] = "Lower lobe of lung"
    elif data["t_ct_loc"] == "13":
        fhirDict["bodycode"] = "44567001"
        fhirDict["bodydisp"] = "Trachea"
    elif data["t_ct_loc"] == "14":
        fhirDict["bodycode"] = "736637009"
        fhirDict["bodydisp"] = "Structure of Left Bronchus"
    elif data["t_ct_loc"] == "15":
        fhirDict["bodycode"] = "736638004"
        fhirDict["bodydisp"] = "Structure of right Bronchus"
    elif data["t_ct_loc"] == "16":
        fhirDict["bodycode"] = "385432009"
        fhirDict["bodydisp"] = "Not Applicable (LUL+LLL)"
    elif data["t_ct_loc"] == "17":
        fhirDict["bodycode"] = "736638004"
        fhirDict["bodydisp"] = "Right Bronchus"
    elif data["t_ct_loc"] == "18":
        fhirDict["bodycode"] = "736637009"
        fhirDict["bodydisp"] = "Left Bronchus"
    elif data["t_ct_loc"] == "19":
        fhirDict["bodycode"] = "31094006"
        fhirDict["bodydisp"] = "Structure Lobe of Lung"
    else:
        fhirDict["bodycode"] = "261665006"
        fhirDict["bodydisp"] = "Unknown"
    # stage
    if data["stage"] == "1":
        fhirDict["overallstage"] = "73082003"
        fhirDict["overallstagedisp"] = "Clinical Stage IIIA"
    elif data["stage"] == "2":
        fhirDict["overallstage"] = "64062008"
        fhirDict["overallstagedisp"] = "Clinical Stage IIIB"
    else:
        fhirDict["overallstage"] = "261665006"
        fhirDict["overallstagedisp"] = "Unknown"

    # Countpetallg
    # countpet_mediast6g
    return fhirDict


def fhir_post_bundle(base_url, bundle):
    try:
        res = requests.post(base_url, headers={'Content-Type': 'application/json+fhir'}, data=bundle)
        res.raise_for_status()
    except Exception as e:
        logging.error("Failed; failing Bundle was:\n{}".format(bundle))
        raise e


tpl_suffix = '-dstu3'
tplenv = jinja2.Environment(loader=jinja2.FileSystemLoader('%s/templates/' % this))
tpl_patient = tplenv.get_template('patientRadiotherapy.json')
tpl_ConditionLungCancer = tplenv.get_template('Condition-LungCancer.json')
tpl_obsBMI = tplenv.get_template('Observation-bmi.json')
tpl_obsECOG = tplenv.get_template('Observation-ecog.json')
tpl_obsFev = tplenv.get_template('Observation-fev.json')
tpl_obsSmok = tplenv.get_template('Observation-Smok.json')
tpl_bundle = tplenv.get_template('bundle{}.json'.format(tpl_suffix))
tpl_obsTumLoad = tplenv.get_template('Observation-TumLoad.json')
tpl_obsHist = tplenv.get_template("Observation-Histology.json")
tpl_obsTNMStage = tplenv.get_template("Observation-TNMS.json")
tpl_Encounter = tplenv.get_template("Encounter.json")
with io.open('Stage3_anonymizedConverted.csv', 'r') as CSVFile:
    rawData = csv.DictReader(CSVFile)
    head = None
    resources = []
    bundles = []
    i = i1 = i2 = i3 = i4 = i5 = i6 = i7 = i8 = i9 = 1
    push_to = None  # 'http://localhost:5000/baseDstu3/'
    bundle_per_patient = False
    for row in rawData:
        data = populate_Data(row, fhirDict)

        # Patient Resources
        jsonDataPat = tpl_patient.render(pat_id=data['pat_id'], gender=data['gender'], birthDate=data['birthDate'],
                                         deceasedBoolean=data['deceasedBoolean'])
        # Encounter
        encounter_id = data["pat_id"]
        jsondataEncounter = tpl_Encounter.render(encounter_id=encounter_id, pat_id=data["pat_id"])

        # Observation- BMI
        bmiid = "bmi" + data["pat_id"]
        jsonDataObsBmi = tpl_obsBMI.render(bmi_id=bmiid, pat_id=data['pat_id'], bmi_val=data['bmi'])

        # Observation - ECOG
        ecogid = "ecog" + data["pat_id"]
        jsonDataObsEcog = tpl_obsECOG.render(obsEcog_id=ecogid, pat_id=data['pat_id'], code=data['ecog'],
                                             disp_val=data['ecogText'])
        # Observation - FEV
        fevid = "fev" + data["pat_id"]
        jsonDataObsFev = tpl_obsFev.render(obsFev_id=fevid, pat_id=data['pat_id'], fev_val=data['fev1'])
        # Observation smokingstatus
        smokstatid = "smokstat"+data["pat_id"]
        jsonDataObssmok=tpl_obsSmok.render(smok_id=smokstatid, pat_id = data['pat_id'],statCode=data['smok_stat'],disp_text=data['smok-statText'])
        # Observation TumorLoad(GTV)
        tumload_id = "TumorLoad" + data["pat_id"]
        jsonDataObsTumLoad = tpl_obsTumLoad.render(obsTumLoad_id=tumload_id, value=data["tumorload"], pat_id=data["pat_id"])
        # Observation Histology
        hist_id = "Histology" + data["pat_id"]
        jsonDataObsHist = tpl_obsHist.render(obsHist_id=hist_id, histcode=data["Hist"], histdisp_val=data["Hist_Text"], pat_id=data["pat_id"], encounter_id=encounter_id)

        # Observation TNMStage
        tnm_id = "TNMStage" + data["pat_id"]
        jsonDataObsTNMStage = tpl_obsTNMStage.render(obsTNMStage_id=tnm_id, pat_id=data["pat_id"], code=data["tnmstage"], disp_val=data["tnmstage_text"])

        # Condition Lung Cancer
        condLungCancer_id = "conditionLungCancer" + data["pat_id"]
        jsondataConditionLungCancer = tpl_ConditionLungCancer.render(condLungCancer_id=condLungCancer_id, bodycode=data["bodycode"], bodydisp=data["bodydisp"], pat_id=data["pat_id"], encounter_id=encounter_id, overallstage=data["overallstage"], overallstagedisp=data["overallstagedisp"],obsTNMStage_id=tnm_id, obsHist_id=hist_id, obsTumLoad_id=tumload_id)

        # jsonDataCondition =tpl_condition.render()
        # resources.append(jsonDataPa

        file = "\Generated\Bundle"
        path = os.getcwd()+file

        with open(path+"/patient{}.json".format(i),"w") as f:
            f.write(jsonDataPat)
            i = i+1

        with open(path+"/bmi{}.json".format(i1),"w") as f1:
            f1.write(jsonDataObsBmi)
            i1 = i1+1

        with open(path+"/ecog{}.json".format(i2),"w") as f2:
            f2.write(jsonDataObsEcog)
            i2 = i2+1

        with open(path+"/smok{}.json".format(i3),"w") as f3:
            f3.write(jsonDataObssmok)
            i3 = i3+1

        with open(path + "/fev{}.json".format(i4), "w") as f4:
            f4.write(jsonDataObsFev)
            i4 = i4+1

        with open(path + "/gtv{}.json".format(i5), "w") as f5:
            f5.write(jsonDataObsTumLoad)
            i5 = i5+1

        with open(path + "/hist{}.json".format(i6), "w") as f6:
            f6.write(jsonDataObsHist)
            i6 = i6+1

        with open(path + "/tnmstage{}.json".format(i7), "w") as f7:
            f7.write(jsonDataObsTNMStage)
            i7 = i7+1

        with open(path + "/condlungcancer{}.json".format(i8), "w") as f8:
            f8.write(jsondataConditionLungCancer)
            i8 = i8+1
        with open(path + "/encounter{}.json".format(i9), "w") as f9:
            f9.write(jsondataEncounter)
            i9 = i9+1