import pandas as pd
import duckdb
from clean_attributes import clean_transfers, clean_microbiologyevents, clean_emar

patients = pd.read_csv("data/patients.csv.gz")
admissions = pd.read_csv("data/admissions.csv.gz", parse_dates=["admittime", "dischtime", "deathtime", "edregtime", "edouttime"])
diagnoses = pd.read_csv("data/diagnoses_icd.csv.gz")
d_icd_diagnoses = pd.read_csv("data/d_icd_diagnoses.csv.gz")
procedures = pd.read_csv("data/procedures_icd.csv.gz", parse_dates=["chartdate"])
d_icd_procedures = pd.read_csv("data/d_icd_procedures.csv.gz")
prescriptions = pd.read_csv("data/prescriptions.csv.gz", parse_dates=["starttime", "stoptime"])
services = pd.read_csv("data/services.csv.gz", parse_dates=["transfertime"])
hcpcsevents = pd.read_csv("data/hcpcsevents.csv.gz", parse_dates=["chartdate"])
transfers=pd.read_csv("data/transfers.csv.gz",parse_dates=["intime","outtime"])
microbiologyevents=pd.read_csv("data/microbiologyevents.csv.gz",parse_dates=["chartdate","charttime","storedate","storetime"] )
emar=pd.read_csv("data/emar.csv.gz",parse_dates=["charttime","scheduletime","storetime"])
transfers_clean = clean_transfers(transfers, admissions)
microbiologyevents_clean = clean_microbiologyevents(microbiologyevents, transfers, admissions)
emar_clean = clean_emar(emar, transfers)



def check_integrity_sql(child_df, parent_df, key, child_table, parent_table):
    query = f"""
        SELECT COUNT(*) AS nb_orphelins
        FROM child_df
        LEFT JOIN parent_df ON child_df.{key} = parent_df.{key}
        WHERE parent_df.{key} IS NULL
    """
    result = duckdb.query(query).to_df()
    nb = result["nb_orphelins"][0]
    if nb > 0:
        raise ValueError(f"{child_table} : {nb} valeurs de {key} absentes de {parent_table}")
    print(f"Intégrité {child_table} -> {parent_table} sur {key} : OK")


def check_integrity_sql_double_key(child_df, parent_df, keys, child_table, parent_table):
    condition_jointure = " AND ".join([f"child_df.{k} = parent_df.{k}" for k in keys])
    condition_null = " AND ".join([f"parent_df.{k} IS NULL" for k in keys])
    query = f"""
        SELECT COUNT(*) AS nb_orphelins
        FROM child_df
        LEFT JOIN parent_df ON {condition_jointure}
        WHERE {condition_null}
    """
    result = duckdb.query(query).to_df()
    nb = result["nb_orphelins"][0]
    if nb > 0:
        raise ValueError(f"{child_table} : {nb} lignes sans correspondance dans {parent_table} sur {keys}")
    print(f"Intégrité {child_table} -> {parent_table} sur {keys} : OK")


def check_all_cross_table():
    check_integrity_sql(admissions, patients, "subject_id", "admissions", "patients")
    check_integrity_sql(diagnoses, admissions, "hadm_id", "diagnoses_icd", "admissions")
    check_integrity_sql(diagnoses, patients, "subject_id", "diagnoses_icd", "patients")
    check_integrity_sql(procedures, admissions, "hadm_id", "procedures_icd", "admissions")
    check_integrity_sql(prescriptions, admissions, "hadm_id", "prescriptions", "admissions")
    check_integrity_sql(transfers_clean, admissions, "hadm_id", "transfers", "admissions")  # brut, sans nettoyage
    check_integrity_sql(services, admissions, "hadm_id", "services", "admissions")
    check_integrity_sql(emar_clean, admissions, "hadm_id", "emar", "admissions")  # brut, sans nettoyage
    check_integrity_sql(hcpcsevents, admissions, "hadm_id", "hcpcsevents", "admissions")
    check_integrity_sql(microbiologyevents_clean, admissions, "hadm_id", "microbiologyevents", "admissions")
    check_integrity_sql_double_key(diagnoses, d_icd_diagnoses, ["icd_code", "icd_version"], "diagnoses_icd", "d_icd_diagnoses")
    check_integrity_sql_double_key(procedures, d_icd_procedures, ["icd_code", "icd_version"], "procedures_icd", "d_icd_procedures")

    print("\nToutes les vérifications d'intégrité ont réussi")


check_all_cross_table()
# transfers_orphelins = transfers[~transfers["hadm_id"].isin(admissions["hadm_id"])]
# print(transfers_orphelins["hadm_id"].isnull().sum())  # combien de hadm_id sont carrément vides
# print(transfers_orphelins["eventtype"].value_counts())  # quel type d'événement domine