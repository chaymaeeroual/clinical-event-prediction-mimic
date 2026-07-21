import pandas as pd 
import duckdb

transfers=pd.read_csv("data/transfers.csv.gz",parse_dates=["intime","outtime"])
admissions=pd.read_csv("data/admissions.csv.gz",parse_dates=["admittime","dischtime","deathtime","edregtime","edouttime"])
emar=pd.read_csv("data/emar.csv.gz",parse_dates=["charttime","scheduletime","storetime"])
microbiologyevents=pd.read_csv("data/microbiologyevents.csv.gz",parse_dates=["chartdate","charttime","storedate","storetime"])

def clean_transfers(transfers, admissions):
    orphelins = transfers[transfers["hadm_id"].isnull()]
    orphelins_ed = orphelins[orphelins["eventtype"] == "ED"]
    orphelins_autres = orphelins[orphelins["eventtype"] != "ED"]
    
    if len(orphelins_autres) > 0:
        raise ValueError(f"transfers : {len(orphelins_autres)} lignes non expliquées par ED")
    
    cleaned_transfers = transfers[transfers["hadm_id"].notnull()]
    print(f"transfers nettoyés : {len(cleaned_transfers)} sur {len(transfers)}")
    return cleaned_transfers
# transfers_clean= clean_transfers(transfers, admissions)
# print(transfers_clean)  


def clean_microbiologyevents(microbiologyevents, transfers, admissions):
    patients_ed = set(transfers[transfers["eventtype"] == "ED"]["subject_id"])
    
    orphelins = microbiologyevents[microbiologyevents["hadm_id"].isnull()]
    orphelins_ed = orphelins[orphelins["subject_id"].isin(patients_ed)]
    orphelins_hors_ed = orphelins[~orphelins["subject_id"].isin(patients_ed)]
    
    # Vérifier que les patients hors ED ont bien au moins un séjour (prélèvement ambulatoire)
    patients_hors_ed = set(orphelins_hors_ed["subject_id"].unique())
    patients_avec_sejour = set(admissions["subject_id"].unique())
    sans_aucun_sejour = patients_hors_ed - patients_avec_sejour
    
    if sans_aucun_sejour:
        raise ValueError(f"microbiologyevents : {len(sans_aucun_sejour)} patients sans aucun séjour connu")
    
    cleaned_microbiologyevents = microbiologyevents[microbiologyevents["hadm_id"].notnull()]
    print(f"microbiologyevents nettoyés : {len(cleaned_microbiologyevents)} sur {len(microbiologyevents)}")
    print(f"  → {len(orphelins_ed)} lignes ED, {len(orphelins_hors_ed)} lignes ambulatoires (patient avec séjour ailleurs)")
    return cleaned_microbiologyevents
# microbiologyevents_clean = clean_microbiologyevents(microbiologyevents, transfers, admissions)
# print(microbiologyevents_clean)  


def clean_emar(emar, transfers):
    patients_ed = set(transfers[transfers["eventtype"] == "ED"]["subject_id"])
    
    orphelins = emar[emar["hadm_id"].isnull()]
    orphelins_ed = orphelins[orphelins["subject_id"].isin(patients_ed)]
    orphelins_autres = orphelins[~orphelins["subject_id"].isin(patients_ed)]
    
    if len(orphelins_autres) > 0:
        raise ValueError(f"emar : {len(orphelins_autres)} lignes hadm_id non expliquées par ED")
    
    # Vérification supplémentaire : chaque patient a bien au moins un médicament identifié
    patients_avec_medication = set(emar[emar["medication"].notnull()]["subject_id"].unique())
    tous_patients = set(emar["subject_id"].unique())
    sans_medicament = tous_patients - patients_avec_medication
    
    if sans_medicament:
        raise ValueError(f"emar : {len(sans_medicament)} patients sans aucun médicament identifié")
    
    cleaned_emar = emar[emar["hadm_id"].notnull()]
    print(f"emar nettoyés : {len(cleaned_emar)} sur {len(emar)}")
    print(f"Vérifié : tous les patients ont au moins un médicament identifié")
    return cleaned_emar
# emar_clean = clean_emar(emar, transfers)
# print(emar_clean)