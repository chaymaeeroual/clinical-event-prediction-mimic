from pathlib import Path
import pandas as pd  

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

#  CHARGEMENT DES DONNÉES
import pandas as pd

def load_data():
    admissions = pd.read_csv(DATA_DIR / "admissions.csv.gz", parse_dates=["admittime", "dischtime", "deathtime", "edregtime", "edouttime"])
    d_icd_diagnoses = pd.read_csv(DATA_DIR / "d_icd_diagnoses.csv.gz")
    d_icd_procedures = pd.read_csv(DATA_DIR / "d_icd_procedures.csv.gz")
    diagnoses_icd = pd.read_csv(DATA_DIR / "diagnoses_icd.csv.gz")
    emar = pd.read_csv(DATA_DIR / "emar.csv.gz", parse_dates=["charttime", "scheduletime", "storetime"])
    hcpcsevents = pd.read_csv(DATA_DIR / "hcpcsevents.csv.gz", parse_dates=["chartdate"])
    microbiologyevents = pd.read_csv(DATA_DIR / "microbiologyevents.csv.gz", parse_dates=["chartdate", "charttime", "storedate", "storetime"])
    patients = pd.read_csv(DATA_DIR / "patients.csv.gz")
    prescriptions = pd.read_csv(DATA_DIR / "prescriptions.csv.gz", parse_dates=["starttime", "stoptime"])
    procedures_icd = pd.read_csv(DATA_DIR / "procedures_icd.csv.gz", parse_dates=["chartdate"])
    services = pd.read_csv(DATA_DIR / "services.csv.gz", parse_dates=["transfertime"])
    transfers = pd.read_csv(DATA_DIR / "transfers.csv.gz", parse_dates=["intime", "outtime"])

    return {
        "admissions": admissions,
        "d_icd_diagnoses": d_icd_diagnoses,
        "d_icd_procedures": d_icd_procedures,
        "diagnoses_icd": diagnoses_icd,
        "emar": emar,
        "hcpcsevents": hcpcsevents,
        "microbiologyevents": microbiologyevents,
        "patients": patients,
        "prescriptions": prescriptions,
        "procedures_icd": procedures_icd,
        "services": services,
        "transfers": transfers,
    }




# FONCTIONS GÉNÉRIQUES
def check_completness(df, colonne, table):
    for i in colonne:
        if df[i].isnull().any():
            raise ValueError(f"{table} : valeurs manquantes dans {i}")
    print("completness:check")
def check_uniqueness(df,colonne,table):
    if df.duplicated(subset=colonne).any():
        raise ValueError(f"{table}:doublons non desiree dans {colonne}")
    print("uniqeness:check")
def check_validity_rang(df,colonne,val_min,val_max,table):
    invalides=df[(df[colonne]>val_max)|(df[colonne]<val_min)]
    if len(invalides)>0:
        raise ValueError(f"{table}:valeur hors plage {colonne}")
    print("validityrang:check")
def check_validity_valueautor(df,colonne,valeursautorise,table):
    invalides=~df[colonne].isin(valeursautorise)
    if invalides.any():
        raise ValueError(f"{table}:valeurs non autorise{colonne}")
    print("validityvalue:check")
def check_comparaison_date(df,col1,col2,table):                       
    invalides=df[df[col1]>df[col2]]
    if len(invalides)>0:
        raise ValueError(f"{table}:pas de coherence entre  les donnees")
    print("comparaison_date:check")
def check_at_least_one_value_per_group(df, group_col, value_col, table):
    groupes_avec_valeur = set(df[df[value_col].notnull()][group_col].unique())
    tous_les_groupes = set(df[group_col].unique())
    groupes_sans_valeur = tous_les_groupes - groupes_avec_valeur
    if groupes_sans_valeur:
        raise ValueError(f"{table} : {len(groupes_sans_valeur)} {group_col} sans aucune valeur dans {value_col}")
    print(f"{table} : chaque {group_col} a au moins une valeur dans {value_col}")



# admissions
def check_completness_admissions(df):
    check_completness(df,["subject_id","hadm_id","admittime","dischtime"],"admissions")
def check_validity_admissions(df):
    if df["subject_id"].dtype!="int64" or df["hadm_id"].dtype!="int64":
        raise ValueError(f"id invalid")
    colonne=["admittime","dischtime","deathtime","edregtime","edouttime"]
    for val in colonne :
        if df[val].dtype!="datetime64[ns]":
            raise ValueError(f"admissions : {val} n'est pas de type date")
    check_validity_valueautor(df,"hospital_expire_flag",(0,1),"admissions")  
    print("validity: complétude OK ")
def check_consistency_admissions(df):
    check_comparaison_date(df,"admittime","dischtime","admissions")
    check_comparaison_date(df,"edregtime","edouttime","admissions")
    print("consistency:coherence ok")
def check_uniqueness_admissions(df):
    check_uniqueness(df,["subject_id","hadm_id"],"admissions")



# d_icd_diagnoses
def check_completness_d_icd_diagnoses(df):
    check_completness(df, ["icd_code", "icd_version"], "d_icd_diagnoses")
    print("d_icd_diagnoses : complétude OK")
def check_uniqueness_d_icd_diagnoses(df):
    check_uniqueness(df, ["icd_code", "icd_version"], "d_icd_diagnoses")
    print("d_icd_diagnoses : unicité OK")
def check_validity_d_icd_diagnoses(df):
    check_validity_valueautor(df, "icd_version", (9, 10), "d_icd_diagnoses")
    print("d_icd_diagnoses : validity OK")



# d_icd_procedures
def check_completness_d_icd_procedures(df):
    check_completness(df, ["icd_code", "icd_version"], "d_icd_diagnoses")
    print("d_icd_procedures : complétude OK")
def check_uniqueness_d_icd_procedures(df):
    check_uniqueness(df, ["icd_code", "icd_version"] ,"d_icd_diagnoses")
    print("d_icd_procedures : unicité OK")
def check_validity_d_icd_procedures(df):
    check_validity_valueautor(df, "icd_version", (9, 10), "d_icd_diagnoses")
    print("d_icd_procedures : validity OK")



# diagnoses_icd
def check_validity_diagnoses_icd(df):
    check_validity_valueautor(df,"icd_version",(9,10),"diagnoses_icd")
def check_completess_diagnoses_icd(df):
    check_completness(df,["subject_id","icd_code","icd_version"],"diagnoses_icd")
def check_uniqueness_diagnoses_icd(df):
    check_uniqueness(df, ["subject_id", "hadm_id", "icd_code", "icd_version","seq_num"], "diagnoses_icd")



# emar
def check_completness_emar(df):
    check_completness(df,["subject_id",  "emar_id", "charttime"], "emar")
    check_at_least_one_value_per_group(df,"subject_id", "medication", "emar")
    print("emar : complétude OK")
def check_uniqueness_emar(df):
    check_uniqueness(df, ["emar_id"], "emar")
    print("emar : unicité OK")
def check_accuracy_emar(df):
    if not pd.api.types.is_numeric_dtype(df["subject_id"]) or not pd.api.types.is_numeric_dtype(df["hadm_id"]):
        raise ValueError("emar : id invalide")
    if df["charttime"].dtype != "datetime64[ns]":
        raise ValueError("emar : charttime n'est pas de type date")
    print("emar : accuracy OK")



# hcpcsevents
def check_uniqueness_hcpcsevents(df):
    check_uniqueness(df,["subject_id","hadm_id","hcpcs_cd","seq_num"],"hcpcsevents")
def check_completness_hcpcsevents(df):
    check_completness(df,["subject_id","hadm_id","hcpcs_cd","seq_num","chartdate"],"hcpcsevents")
def check_validity_hcpcsevents(df):
    if df["chartdate"].dtype != "datetime64[ns]":
        raise ValueError("chartdate:ne convient pas ")
    print("validity:check")



# microbiologyevents
def check_uniqueness_microbiologyevents(df):
    check_uniqueness(df,["microevent_id","subject_id","micro_specimen_id"],"microbiologyevents")
def check_completness_microbiologyevents(df):
    check_completness(df,["microevent_id","subject_id","micro_specimen_id","chartdate","spec_itemid","spec_type_desc","test_itemid","test_name"],"microbiologyevents")
def check_validity_microbiologyevents(df):
    if df["chartdate"].dtype != "datetime64[ns]":
        raise ValueError("chartdate:ne convient pas ")
    print("validity:check")



# patients
def check_uniqueness_patients(df):
    check_uniqueness(df,["subject_id"],"patients")
def check_completesse_patients(df):
    check_completness(df,["subject_id"],"patients")
def check_validity_patients(df):
    check_validity_rang(df,"anchor_age",0,150,"patients")

    

# prescriptions
def check_uniqueness_prescriptions(df):
    check_uniqueness(df,["subject_id","hadm_id","pharmacy_id","drug"],"prescriptions")
def check_completness_prescriptions(df):
    check_completness(df,["subject_id","hadm_id","pharmacy_id","starttime","drug","drug_type",],"prescriptions")
def check_validity_prescriptions(df):
    if df["starttime"].dtype!="datetime64[ns]":
        raise ValueError("starttime:type pas coatible")
    if df["stoptime"].dtype!="datetime64[ns]":
        raise ValueError("stoptime:type pas coatible")   
    print("validity:check")



#procedure_icd
def check_validity_procedure_icd(df):
    check_validity_valueautor(df,"icd_version",(9,10),"procedures_icd")
    if df["chartdate"].dtype != "datetime64[ns]":
        raise ValueError("colonne non valide")
def check_completess_diagnoses_icd(df):
    check_completness(df,["subject_id","hadm_id"],"procedures_icd")
def check_uniqueness_procedures_icd(df):
    check_uniqueness(df,["subject_id", "hadm_id", "icd_code", "icd_version","seq_num"],"procedures_icd")



#transfert
def check_completness_transfert(df):
    check_completness(df,["subject_id","transfer_id", "eventtype"],"transfert")
def check_validity_transfert(df):
    if df["intime"].dtype != "datetime64[ns]":
        raise ValueError("transfers : intime n'est pas de type date")
    if df["outtime"].dtype != "datetime64[ns]":
        raise ValueError("transfers : outtime n'est pas de type date")
    print("validity:check")
def check_uniqueness_transfert(df):
    check_uniqueness(df,["transfer_id"],"transferts")



# services
def check_uniqueness_services(df):
    check_uniqueness(df,["subject_id","hadm_id","transfertime"],"services")
def check_completness_services(df):
    check_completness(df,["subject_id","hadm_id","curr_service"],"services")
def check_validity_services(df):
    if df["transfertime"].dtype!="datetime64[ns]":
        raise ValueError("transfertime:type non convenable")
    print("validity:check")





def run_data_quality():
   
  tables = load_data()

  admissions = tables["admissions"]
  d_icd_diagnoses = tables["d_icd_diagnoses"]
  d_icd_procedures =tables["d_icd_procedures"]
  diagnoses_icd =tables["diagnoses_icd"]
  emar = tables["emar"]
  hcpcsevents = tables["hcpcsevents"]   
  microbiologyevents = tables["microbiologyevents"]
  patients = tables["patients"]
  prescriptions = tables["prescriptions"]
  procedures_icd = tables["procedures_icd"]
  transfers = tables["transfers"]
  services = tables["services"]

   
  check_completness_admissions(admissions)
  check_validity_admissions(admissions)
  check_consistency_admissions(admissions)
  check_uniqueness_admissions(admissions)

  check_completness_d_icd_diagnoses(d_icd_diagnoses)
  check_uniqueness_d_icd_diagnoses(d_icd_diagnoses)
  check_validity_d_icd_diagnoses(d_icd_diagnoses)

  check_completness_d_icd_procedures(d_icd_procedures)
  check_uniqueness_d_icd_procedures(d_icd_procedures)
  check_validity_d_icd_procedures(d_icd_procedures)  

  check_validity_diagnoses_icd(diagnoses_icd)
  check_completess_diagnoses_icd(diagnoses_icd)
  check_uniqueness_diagnoses_icd(diagnoses_icd)

  check_completness_emar(emar)
  check_uniqueness_emar(emar)
  check_accuracy_emar(emar)

  check_uniqueness_hcpcsevents(hcpcsevents)
  check_completness_hcpcsevents(hcpcsevents)
  check_validity_hcpcsevents(hcpcsevents)

  check_uniqueness_microbiologyevents(microbiologyevents)
  check_completness_microbiologyevents(microbiologyevents)
  check_validity_microbiologyevents(microbiologyevents)

  check_uniqueness_patients(patients)
  check_completesse_patients(patients)
  check_validity_patients(patients)

  check_uniqueness_prescriptions(prescriptions)
  check_completness_prescriptions(prescriptions)
  check_validity_prescriptions(prescriptions)

  check_validity_procedure_icd(procedures_icd)
  check_completess_diagnoses_icd(procedures_icd)
  check_uniqueness_procedures_icd(procedures_icd)

  check_completness_transfert(transfers)
  check_validity_transfert(transfers)
  check_uniqueness_transfert(transfers)

  check_uniqueness_services(services)
  check_completness_services(services)
  check_validity_services(services)

  print("Data Quality terminée avec succès.")