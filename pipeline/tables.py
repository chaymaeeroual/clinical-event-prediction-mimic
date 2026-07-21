from pathlib import Path
import pandas as pd  

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

from .clean_attributes import (
    clean_transfers,
    clean_microbiologyevents,
    clean_emar
)

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



def tables_cleaning():
    patients = pd.read_csv(DATA_DIR / "patients.csv.gz")
    admissions = pd.read_csv(DATA_DIR / "admissions.csv.gz", parse_dates=["admittime", "dischtime", "deathtime", "edregtime", "edouttime"])
    diagnoses_icd= pd.read_csv(DATA_DIR / "diagnoses_icd.csv.gz")
    d_icd_diagnoses = pd.read_csv(DATA_DIR / "d_icd_diagnoses.csv.gz")
    procedures_icd= pd.read_csv(DATA_DIR / "procedures_icd.csv.gz", parse_dates=["chartdate"])
    d_icd_procedures = pd.read_csv(DATA_DIR / "d_icd_procedures.csv.gz")
    prescriptions = pd.read_csv(DATA_DIR / "prescriptions.csv.gz", parse_dates=["starttime", "stoptime"])
    services = pd.read_csv(DATA_DIR / "services.csv.gz", parse_dates=["transfertime"])
    hcpcsevents = pd.read_csv(DATA_DIR / "hcpcsevents.csv.gz", parse_dates=["chartdate"])
    transfers=pd.read_csv(DATA_DIR / "transfers.csv.gz",parse_dates=["intime","outtime"])
    microbiologyevents=pd.read_csv(DATA_DIR / "microbiologyevents.csv.gz",parse_dates=["chartdate","charttime","storedate","storetime"] )
    emar=pd.read_csv(DATA_DIR / "emar.csv.gz",parse_dates=["charttime","scheduletime","storetime"])
    transfers_cleann = clean_transfers(transfers, admissions)
    microbiologyevents_cleann = clean_microbiologyevents(microbiologyevents, transfers, admissions)
    emar_cleann = clean_emar(emar, transfers)
    return {
        "patients": patients,
        "admissions": admissions,
        "d_icd_diagnoses": d_icd_diagnoses,
        "d_icd_procedures": d_icd_procedures,
        "diagnoses_icd": diagnoses_icd,
        "emar": emar,
        "hcpcsevents": hcpcsevents,
        "microbiologyevents": microbiologyevents,
        "prescriptions": prescriptions,
        "procedures_icd": procedures_icd,
        "services": services,
        "transfers": transfers,
        "transfers_cleann": transfers_cleann,
        "microbiologyevents_cleann": microbiologyevents_cleann,
        "emar_cleann": emar_cleann
    }