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
keys = ['pat_id', 'gender', 'birthDate', 'deceasedBoolean', 'stage', 'ecog', 'ecogText', 'smok_stat', 'smok-statText','fev1', 'gtv1']
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
    # Get the Condition/ Stage Information
    if data['stage'] == '1':
        fhirDict['stage'] = 'III A'
    elif data['stage'] == '2':
        fhirDict['stage'] = 'III B'
    else:
        fhirDict['stage'] = 'Not Specified'
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
        fhirDict['ecog'] = 'Not Specified'
    # Observation - Smoking Status
    if data['dumsmok2'] == '1':
        fhirDict['smok_stat'] = '446172000'
        fhirDict['smok-statText']="Never/ex smoker"
    if data['dumsmok2'] == '2':
        fhirDict['smok_stat'] = '8392000'
        fhirDict['smok-statText'] = "Current Smoker"
    else:
        fhirDict['smok_stat'] = 'Not Specified'
        fhirDict['smok-statText'] = "Not Specified"
    # Observation - BMI
    fhirDict['bmi'] = data['bmi']
    # FEV1
    fhirDict['fev1'] = data['fev1pc_t0']
    # Histology - observation
    # tstage - observation
    # nstage - observation
    # gtv - observation
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
tpl_condition = tplenv.get_template('Condition-LungCancer.json')
tpl_obsBMI = tplenv.get_template('Observation-bmi.json')
tpl_obsECOG = tplenv.get_template('Observation-ecog.json')
tpl_obsFev = tplenv.get_template('Observation-fev.json')
tpl_obsSmok = tplenv.get_template('Observation-Smok.json')
tpl_bundle = tplenv.get_template('bundle{}.json'.format(tpl_suffix))
tpl_obsTumLoad = tplenv.get_template('Observation-TumLoad.json')
with io.open('Stage3_anonymizedConverted.csv', 'r') as CSVFile:
    rawData = csv.DictReader(CSVFile)
    head = None
    resources = []
    bundles = []
    i = i1 = i2 = i3 = i4 = i5 = 1
    push_to = None  # 'http://localhost:5000/baseDstu3/'
    bundle_per_patient = False
    for row in rawData:
        data = populate_Data(row, fhirDict)

        # Patient Resources
        jsonDataPat = tpl_patient.render(pat_id=data['pat_id'], gender=data['gender'], birthDate=data['birthDate'],
                                         deceasedBoolean=data['deceasedBoolean'])

        # Observation- BMI
        bmiid = data["pat_id"]
        jsonDataObsBmi = tpl_obsBMI.render(bmi_id=bmiid, pat_id=data['pat_id'], bmi_val=data['bmi'])

        # Observation - ECOG
        ecogid = "ecog" + data["pat_id"]
        jsonDataObsEcog = tpl_obsECOG.render(obsEcog_id=ecogid, pat_id=data['pat_id'], code=data['ecog'],
                                             disp_val=data['ecogText'])
        # Observation - FEV
        fevid = "fev" + data["pat_id"]
        jsonDataObsFev = tpl_obsFev.render(obsFev_id=fevid, pat_id=data['pat_id'], fev_val=data['fev1'])

        smokstatid = "smokstat"+data["pat_id"]
        jsonDataObssmok=tpl_obsSmok.render(smok_id=smokstatid, pat_id = data['pat_id'],statCode =data['smok_stat'],disp_text=data['smok-statText'])

        obsTumLoad_id = "öbsTumorLoad" + data["pat_id"]
        tumorload = data['gtv1']
        jsonDataObsTumLoad = tpl_obsTumLoad.render(obsTumorLoad_id= obsTumLoad_id, value= tumorload)

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

        with open(path + "/fev{}.json".format(i3), "w") as f4:
            f4.write(jsonDataObsFev)
            i4 = i4+1

        with open(path + "/gtv{}.json".format(i3), "w") as f5:
            f5.write(jsonDataObsTumLoad)
            i5 = i5+1