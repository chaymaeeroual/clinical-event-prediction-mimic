import pandas as pd
import duckdb



def admissions_joiture(admissions_df):
    con = duckdb.connect()
    con.register("admissions", admissions_df)
    query = """
        SELECT subject_id, hadm_id, 'admission' AS event_type, admittime AS event_time,
               admission_type AS event_value, NULL AS order_hint,
               admit_provider_id AS provider_id, admission_location AS event_location
        FROM admissions
        WHERE admittime IS NOT NULL

        UNION ALL

        SELECT subject_id, hadm_id, 'discharge' AS event_type, dischtime AS event_time,
               NULL AS event_value, NULL AS order_hint,
               admit_provider_id AS provider_id, discharge_location AS event_location
        FROM admissions
        WHERE dischtime IS NOT NULL

        UNION ALL

        SELECT subject_id, hadm_id, 'death' AS event_type, deathtime AS event_time,
               NULL AS event_value, NULL AS order_hint,
               NULL AS provider_id, NULL AS event_location
        FROM admissions
        WHERE deathtime IS NOT NULL
    """
    return con.execute(query).fetchdf()
# admissions_events = admissions_joiture(tables["admissions"])
# print(admissions_events.head())



def diagnoses_joiture(diagnoses_df, d_icd_diagnoses_df, admissions_df):
    con = duckdb.connect()
    con.register("diagnoses_icd", diagnoses_df)
    con.register("d_icd_diagnoses", d_icd_diagnoses_df)
    con.register("admissions", admissions_df)
    query = """
        SELECT d.subject_id, d.hadm_id, 'diagnosis' AS event_type,
               a.admittime AS event_time, l.long_title AS event_value,
               d.seq_num AS order_hint, NULL AS provider_id, NULL AS event_location
        FROM diagnoses_icd d
        JOIN admissions a ON d.hadm_id = a.hadm_id
        LEFT JOIN d_icd_diagnoses l ON d.icd_code = l.icd_code AND d.icd_version = l.icd_version
    """
    return con.execute(query).fetchdf()


def procedures_joiture(procedures_df, d_icd_procedures_df):
    con = duckdb.connect()
    con.register("procedures_icd", procedures_df)
    con.register("d_icd_procedures", d_icd_procedures_df)
    query = """
        SELECT p.subject_id, p.hadm_id, 'procedure' AS event_type,
               p.chartdate AS event_time, l.long_title AS event_value,
               p.seq_num AS order_hint, NULL AS provider_id, NULL AS event_location
        FROM procedures_icd p
        LEFT JOIN d_icd_procedures l ON p.icd_code = l.icd_code AND p.icd_version = l.icd_version
    """
    return con.execute(query).fetchdf()


def prescriptions_joiture(prescriptions_df):
    con = duckdb.connect()
    con.register("prescriptions", prescriptions_df)
    query = """
        SELECT subject_id, hadm_id, 'prescription' AS event_type,
               starttime AS event_time, drug AS event_value,
               NULL AS order_hint, order_provider_id AS provider_id, NULL AS event_location
        FROM prescriptions
        WHERE starttime IS NOT NULL
    """
    return con.execute(query).fetchdf()


def transfers_joiture(transfers_cleann_df):
    con = duckdb.connect()
    con.register("transfers", transfers_cleann_df)
    query = """
        SELECT subject_id, hadm_id, 'transfer' AS event_type,
               intime AS event_time, eventtype AS event_value,
               NULL AS order_hint, NULL AS provider_id, careunit AS event_location
        FROM transfers
    """
    return con.execute(query).fetchdf()


def emar_joiture(emar_cleann_df):
    con = duckdb.connect()
    con.register("emar", emar_cleann_df)
    query = """
        SELECT subject_id, hadm_id, 'medication_administration' AS event_type,
               charttime AS event_time, medication AS event_value,
               NULL AS order_hint, enter_provider_id AS provider_id, NULL AS event_location
        FROM emar
        WHERE charttime IS NOT NULL
    """
    return con.execute(query).fetchdf()


def hcpcsevents_joiture(hcpcsevents_df):
    con = duckdb.connect()
    con.register("hcpcsevents", hcpcsevents_df)
    query = """
        SELECT subject_id, hadm_id, 'hcpcs_act' AS event_type,
               chartdate AS event_time, short_description AS event_value,
               seq_num AS order_hint, NULL AS provider_id, NULL AS event_location
        FROM hcpcsevents
    """
    return con.execute(query).fetchdf()


def microbiologyevents_joiture(microbiologyevents_cleann_df):
    con = duckdb.connect()
    con.register("microbiologyevents", microbiologyevents_cleann_df)
    query = """
        SELECT subject_id, hadm_id, 'microbiology_result' AS event_type,
               chartdate AS event_time,
               COALESCE(org_name || ' - ' || ab_name || ' - ' || interpretation, test_name) AS event_value,
               NULL AS order_hint, NULL AS provider_id, NULL AS event_location
        FROM microbiologyevents
    """
    return con.execute(query).fetchdf()




def build_all_events(tables, transfers_clean, emar_clean, micro_clean):
    admissions = tables["admissions"]

    events = pd.concat([
        admissions_joiture(admissions),
        diagnoses_joiture(tables["diagnoses_icd"], tables["d_icd_diagnoses"], admissions),
        procedures_joiture(tables["procedures_icd"], tables["d_icd_procedures"]),
        prescriptions_joiture(tables["prescriptions"]),
        transfers_joiture(transfers_clean),
        emar_joiture(emar_clean),
        hcpcsevents_joiture(tables["hcpcsevents"]),
        microbiologyevents_joiture(micro_clean),
    ], ignore_index=True)

    # Tri chronologique : d'abord par patient/séjour, puis par temps réel,
    # puis par order_hint (seq_num) pour départager les égalités de date
    events = events.sort_values(["subject_id", "hadm_id", "event_time", "order_hint"])

    # Position de chaque événement dans sa séquence
    events["event_position"] = events.groupby(["subject_id", "hadm_id"]).cumcount() + 1

    print(f"Total d'événements construits : {len(events)}")
    print(events["event_type"].value_counts())

    return events