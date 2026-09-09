import pandas as pd
from fuzzywuzzy import fuzz

from dhis2_env import get_api

# Initialize the DHIS2 API. Credentials come from .env (see .env.example).
api = get_api("NG_NCD_ANALYST")

# List of facilities (UID and name)
facilities = [
    {"uid": "YTzOXzb89DL", "name": "kn Akilu Memorial Primary Health Centre"},
    {"uid": "OKTuiOp2exd", "name": "kn Bono Primary Health Centre"},
    {"uid": "P5diOhYEAKP", "name": "kn Bunkure Basic Health Clinic"},
    {"uid": "lVJxBaIIzSH", "name": "kn Burji Primary Heath Centre"},
    {"uid": "JJL8Ukh1ZlZ", "name": "kn Dala Primary Health Care Centre"},
    {"uid": "tcSIgkbW2jA", "name": "kn Dantamashe Primary Health Centre"},
    {"uid": "NdMeho3Y5SL", "name": "kn Darki Primary Health Centre"},
    {"uid": "DUJ4yYCGuUO", "name": "kn Dawakiji Primary Health Center"},
    {"uid": "jpPaQTbjIlU", "name": "kn Dawakin Dakata Primary Health Centre"},
    {"uid": "PuhR3ydarPO", "name": "kn Dawanau Primary Health Centre"},
    {"uid": "kgYGusd1B8r", "name": "kn Ganduje Primary Health Centre"},
    {"uid": "Bk0yIUmb3rl", "name": "kn Gandu Primary Health Centre"},
    {"uid": "bYamdI7FHE5", "name": "kn Gano Primary Health Center"},
    {"uid": "w55xXUS3HNU", "name": "kn Garo Primary Health Centre"},
    {"uid": "tweJXXNQgkA", "name": "kn Getso Cottage Hospital"},
    {"uid": "yoCc0iJ2nTE", "name": "kn Gogel Primary Health Centre"},
    {"uid": "XxWPQe0wlY5", "name": "kn Gurun primary Health Care Centre"},
    {"uid": "xUORgwU22YU", "name": "kn Gwagwarwa Primary Health Centre"},
    {"uid": "JmoqljZnX3K", "name": "kn Gwammaja Maternity And Child Health Clinic"},
    {"uid": "DxfVRX9j8np", "name": "kn Hotoro Arewa Primary Health Centre"},
    {"uid": "ehJsDey0nF2", "name": "kn JaEn Primary Health Centre"},
    {"uid": "YQjx80qS7hF", "name": "kn Jalli Health Primary Health Centre"},
    {"uid": "GHtds741JTH", "name": "kn JaOji Primary Health Centre"},
    {"uid": "aoOPscxu7Tc", "name": "kn Kabuga Primary Health Centre"},
    {"uid": "ucVM5wpYDPw", "name": "kn Kadamu Primary Health Centre"},
    {"uid": "tMV8zSUXnoK", "name": "kn Kafin Agur Primary Health Centre"},
    {"uid": "RVo3p5HjxuK", "name": "kn Kaura Goje Primary Health Centre"},
    {"uid": "tu9DZ2g4LZH", "name": "kn Kofar Ruwa Health Clinic"},
    {"uid": "SPmI1eHa028", "name": "kn Kore Primary Health Center"},
    {"uid": "zGzRBxErbe2", "name": "kn Kumurya Primary Health Centre"},
    {"uid": "UhwUiVzHWsA", "name": "kn Kurna Primary Health Centre"},
    {"uid": "fLyVRxBBmO1", "name": "kn Kwacire Primary Health Centre"},
    {"uid": "O8AiFDEnEqK", "name": "kn Lajawa Primary Health Centre"},
    {"uid": "nltVWcc5JRe", "name": "kn Lambu Primary Health Clinic"},
    {"uid": "PFmp8iIeWRb", "name": "kn Mai-Tsidau Primary Health Centre"},
    {"uid": "p3BLZdzN1nZ", "name": "kn Makoda Primary Health Centre"},
    {"uid": "NLbb5g68GnM", "name": "kn Mariri Primary Health Centre"},
    {"uid": "F9IXHghODzQ", "name": "kn Panshekara Primary Health Centre"},
    {"uid": "DwFXaxsC09L", "name": "kn Rijiyar Lemo Model Primary Health Centre"},
    {"uid": "DwV5TmasIOB", "name": "kn Rimin Gado Primary Health Centre"},
    {"uid": "YRx67oHyw5U", "name": "kn Sabo Garba Maternal and Child Health Clinic"},
    {"uid": "jiBs5Wlznle", "name": "kn Shanono Primary Health Centre"},
    {"uid": "yNtPl1eGwar", "name": "kn Sharada Primary Health Centre"},
    {"uid": "uRzXjHHigm9", "name": "kn Shekar Barde Primary Health Centre"},
    {"uid": "BqwpWi32Gus", "name": "kn Tsanyawa Primary Health Centre"},
    {"uid": "YsZ3eAa7HU1", "name": "kn Tudun Fulani Primary Health Center"},
    {"uid": "rBGMr2mML23", "name": "kn Tukuntawa Primary Health Centre"},
    {"uid": "LTsuanAvTRU", "name": "kn Unguwar Gini Primary Health Centre"},
    {"uid": "WmH9sWwbDGC", "name": "kn Unguwa Uku Primary Health Centre"},
    {"uid": "A5YrqToVCgd", "name": "kn Utai Primary Health Centre"},
    {"uid": "m3YLnlDmRQc", "name": "kn Yalwa Primary Health Centre (DAL)"},
    {"uid": "PAxRf5zY1As", "name": "kn Yargwanda Primary Health Centre"},
    {"uid": "scU9IsGCJ9o", "name": "og Abigi Health Clinic"},
    {"uid": "iPHdxJ2F9ve", "name": "og Adeun Health Clinic"},
    {"uid": "XuQ3oT7hwnc", "name": "og Agbado Primary Health Centre"},
    {"uid": "oK73jmU1jaV", "name": "og Agbara Primary Health Care Centre"},
    {"uid": "BaGCGdYknNN", "name": "og Ajaka Primary Health Centre"},
    {"uid": "Gciekg99hVj", "name": "og Ajigunle Health Clinic"},
    {"uid": "IzsMHp6eB0u", "name": "og Ajuwon Primary Health Centre"},
    {"uid": "HC1R05fpe9j", "name": "og Alabata Heath Clinic"},
    {"uid": "KHNtp8eVI9z", "name": "og Alagbagba Health Clinic"},
    {"uid": "wgbimD4TWvq", "name": "og Alagbon Health Clinic"},
    {"uid": "aGiLgpElLX5", "name": "og Alapako Aro Health Clinic"},
    {"uid": "MRpbUuamXN1", "name": "og Atan Health Centre"},
    {"uid": "IGcFSePMltz", "name": "og Atan Model Primary Health Centre"},
    {"uid": "mPl8BWnKXaA", "name": "og Atikori Health Centre"},
    {"uid": "tmp5ufyijPI", "name": "og Ayeteju Health Centre"},
    {"uid": "AqXvr3M8Ix0", "name": "og Erunwon Health Clinic"},
    {"uid": "o9IDb1gMBqV", "name": "og Iberekodo Primary Health Center"},
    {"uid": "m2DR5doEjKC", "name": "og Ibile Primary Health Centre"},
    {"uid": "lYBdFTtjv8R", "name": "og Ibipe Health Clinic"},
    {"uid": "ACgBmF2uh5h", "name": "og Idiroko Health Centre"},
    {"uid": "b8zi5ST4dH3", "name": "og Igbogila Primary Health Centre"},
    {"uid": "aPRnhePRnpS", "name": "og Ijari Model Health Centre"},
    {"uid": "tMmRVO0UPrc", "name": "og Ikenne Health Clinic"},
    {"uid": "yCtv2Vsc2ck", "name": "og Ilese Health Clinic"},
    {"uid": "c5oQun3S0ut", "name": "og Ilushin Health Clinic"},
    {"uid": "HCSaH6XWQzu", "name": "og Imasayi Primary Health Centre"},
    {"uid": "lSoOduWvZUx", "name": "og Imeko Primary Health Centre"},
    {"uid": "zGBqCQnzKRl", "name": "og Imewuro Health Clinic"},
    {"uid": "I2bRkZthdsN", "name": "og Imushin Health Centre"},
    {"uid": "tpwVdxpVdi0", "name": "og Iperu Health Clinic"},
    {"uid": "lMr57aLPSoT", "name": "og Isaga Owode Health Clinic"},
    {"uid": "QLanNpwrwqb", "name": "og Isara Health Clinic, Idi aba"},
    {"uid": "yzlSMH7AjJ9", "name": "og Isoyin Health Clinic"},
    {"uid": "MtPVEBYLvHZ", "name": "og Ita-Alapo Health care"},
    {"uid": "vzXmhEL6vKp", "name": "og Itamapako Primary Health Center"},
    {"uid": "y80D6bqBTIF", "name": "og Itanarun Health Clinic"},
    {"uid": "UZiTbfwdp7d", "name": "og Ita Osu Health Centre"},
    {"uid": "G80rqi1zuoW", "name": "og Itele Health Centre"},
    {"uid": "S90QvZ5FKEo", "name": "og Itoko Health Post"},
    {"uid": "oAXeCYwch7U", "name": "og Itori Primary Health Care Centre"},
    {"uid": "NvLZ9dM72PS", "name": "og Iwopin Comprehensive Health Centre"},
    {"uid": "yYVUbNRI1ye", "name": "og Iworo Health Clinic"},
    {"uid": "P57Em7aLNYn", "name": "og Iwoye Health Centre"},
    {"uid": "neBNBh5lyU5", "name": "og Keesi Primary Health Centre"},
    {"uid": "o5uazdFDoBc", "name": "og Kugba Health Centre"},
    {"uid": "aaHtdluy0UN", "name": "og Kuto Health Post"},
    {"uid": "WgBme03RfN9", "name": "og Laderin Health Centre"},
    {"uid": "OjhcqZ6O5aK", "name": "og Leslie Primary Health Centre"},
    {"uid": "XMOewxpQvsf", "name": "og Mobalufon Model Health Centre"},
    {"uid": "bSBfEwoHpOQ", "name": "og Mokoloki Health Clinic"},
    {"uid": "WtOaeyRb56h", "name": "og Mowe Health Post"},
    {"uid": "z2syYAAoWvG", "name": "og Obada Health Clinic"},
    {"uid": "S8OFPw6S1An", "name": "og Obada Primary Health Centre"},
    {"uid": "MJdQYF5wfwU", "name": "og Oba Gbadebo Health Clinic"},
    {"uid": "UupnludKN9T", "name": "og Obatonko Health Clinic"},
    {"uid": "bnZRTFMPLCY", "name": "og Ode Primary Health Centre"},
    {"uid": "TYdI1qB6nNd", "name": "og Odo Esa Health Clinic"},
    {"uid": "sjx434GtApM", "name": "og Odoregbe Health Centre"},
    {"uid": "lqP6OJMB7rp", "name": "og Odosebora Health Post"},
    {"uid": "DN6B34Msybh", "name": "og Ofada Primary Health Centre"},
    {"uid": "SSx6C5WTRT0", "name": "og Ogijo Primary Heath Care"},
    {"uid": "lTY0oWxRooI", "name": "og Ojowo Health Clinic"},
    {"uid": "VzyOk9CLz5X", "name": "og Oke-Agbo Health Centre"},
    {"uid": "B4rPVehwpZ9", "name": "og Oke Aje Health Clinic"},
    {"uid": "S84LuOwGZ6R", "name": "og Oke Ilewo Family Health Centre"},
    {"uid": "UJlY2ribPXq", "name": "og Oke-Odo Health Clinic"},
    {"uid": "fLSPCrGZjF5", "name": "og Oke-Oyinbo Family Health Centre"},
    {"uid": "TPh3usnjIA0", "name": "og Olodo Health Clinic"},
    {"uid": "PKf7VHpxmBG", "name": "og Olose Primary Health Centre"},
    {"uid": "WzR3qv4MwnA", "name": "og Oni Health Centre"},
    {"uid": "vJgfsb9nZj7", "name": "og Orile - Ilugun Health Clinic"},
    {"uid": "P3fpoNyT8Vj", "name": "og Osiele Health Clinic"},
    {"uid": "d9NwzZYDm4n", "name": "og Ososa Health Clinic"},
    {"uid": "TUzBaQ3PYDm", "name": "og Otta Primary Health Care Center"},
    {"uid": "AFIkwCI2Sb9", "name": "og Owode Health Clinic"},
    {"uid": "KfdFtlpdbL5", "name": "og Owode Health Clinic"},
    {"uid": "dQE9wQrW9rS", "name": "og Sabo Agura Health Clinic"},
    {"uid": "spFKAo4GHXy", "name": "og Sabo Health Clinic"},
    {"uid": "WqebnzGgb71", "name": "og Sango Primary Health Centre"},
    {"uid": "AJn9FGje5Zp", "name": "og Saraki Adigbe Health Clinic"},
    {"uid": "IOrthr9XBkL", "name": "og Wasimi Health Clinic"}
]

# Attribute UIDs for patient details
ATTRIBUTE_UIDS = {
    "name": "R6VkX5nsAy4",
    "sex": "oindugucx72",
    "phone_number": "YRDy9xy9jD0",
    "dob": "NI0QRzJvQ0k",
}

PROGRAM_UID = "pMIglSEqPGS"# Hypertension program

# Cache to store patient data
patient_cache = {}


def fetch_enrollments(org_unit_uid):
    """Fetch enrollments for a given facility (org unit)."""
    try:
        response = api.get(
            f"tracker/enrollments",
            params={
                "orgUnit": org_unit_uid,
                "skipPaging": "true",
                "enrolledAfter": "2022-12-31",
                "program": PROGRAM_UID
            },
        ).json()
        return response.get("instances", [])
    except Exception as e:
        print(f"Error fetching enrollments for {org_unit_uid}: {e}")
        return []


def fetch_tracked_entity(tei_uid):
    """Fetch tracked entity details for a given UID."""
    if tei_uid in patient_cache:
        return patient_cache[tei_uid]

    try:
        response = api.get(f"tracker/trackedEntities/{tei_uid}").json()
        attributes = response.get("attributes", [])
        patient_data = {
            "name": next(
                (attr["value"] for attr in attributes if attr["attribute"] == ATTRIBUTE_UIDS["name"]), "Not Available"
            ),
            "sex": next(
                (attr["value"] for attr in attributes if attr["attribute"] == ATTRIBUTE_UIDS["sex"]), "Not Available"
            ),
            "phone_number": next(
                (attr["value"] for attr in attributes if attr["attribute"] == ATTRIBUTE_UIDS["phone_number"]),
                "Not Available"
            ),
            "dob": next(
                (attr["value"] for attr in attributes if attr["attribute"] == ATTRIBUTE_UIDS["dob"]), "Not Available"
            ),
        }
        patient_cache[tei_uid] = patient_data
        return patient_data
    except Exception as e:
        print(f"Error fetching tracked entity {tei_uid}: {e}")
        return {"name": "Error", "sex": "Error", "phone_number": "Error", "dob": "Error"}


def fuzzy_similarity(str1, str2):
    """Compute fuzzy similarity between two strings."""
    set1 = set(str1.lower().split())
    set2 = set(str2.lower().split())

    token_similarity = fuzz.token_set_ratio(str1, str2)
    substring_penalty = 0 if set1 != set2 and not (set1.issubset(set2) or set2.issubset(set1)) else -20

    return token_similarity + substring_penalty


def calculate_age(dob):
    """Calculate age using 2025-01-01 as the reference date."""
    try:
        # Ensure that dob is a valid date
        dob_date = pd.to_datetime(dob, errors='coerce')
        if pd.isnull(dob_date):
            return "Not Available"
        reference_date = datetime(2025, 1, 1)
        age = reference_date.year - dob_date.year - ((reference_date.month, reference_date.day) < (dob_date.month, dob_date.day))
        return age
    except Exception as e:
        print(f"Error calculating age for dob {dob}: {e}")
        return "Not Available"



# List to store duplicate results
results = []

# Process each facility
facilities_processed = 0
total_facilities = len(facilities)

for facility in facilities:
    print(f"Processing facility ({facilities_processed + 1}/{total_facilities}): {facility['name']}")

    # Fetch enrollments
    enrollments = fetch_enrollments(facility["uid"])

    # Process each enrollment to build the table
    rows = []
    for enrollment in enrollments:
        tei_uid = enrollment["trackedEntity"]
        enrolled_at = enrollment.get("enrolledAt", "Not Available")
        patient_data = fetch_tracked_entity(tei_uid)

        rows.append({
            "uid": tei_uid,
            "patient_name": patient_data["name"],
            "phone_number": patient_data["phone_number"],
            "sex": patient_data["sex"],
            "dob": patient_data["dob"],
            "facility_name": facility["name"],
            "enrolledAt": enrolled_at,
        })

    # Convert to DataFrame for this facility
    df = pd.DataFrame(rows)

    # Find duplicates within the facility
    unique_sex = df['sex'].unique()

    for j in unique_sex:
        sample = df[df['sex'] == j].reset_index(drop=True)
        if len(sample) > 1:
            duplicate_pairs = []
            for k in range(len(sample)):
                for l in range(k + 1, len(sample)):
                    similarity_score = fuzzy_similarity(sample['patient_name'].iloc[k], sample['patient_name'].iloc[l])
                    if similarity_score > 80:
                        dob1 = sample['dob'].iloc[k]
                        dob2 = sample['dob'].iloc[l]
                        age1 = calculate_age(dob1)
                        age2 = calculate_age(dob2)

                        duplicate_pairs.append((
                            facility["name"],
                            sample['uid'].iloc[k],
                            sample['uid'].iloc[l],
                            sample['patient_name'].iloc[k],
                            sample['patient_name'].iloc[l],
                            sample['phone_number'].iloc[k],
                            sample['phone_number'].iloc[l],
                            dob1,
                            dob2,
                            age1,
                            age2,
                            similarity_score,
                            sample['enrolledAt'].iloc[k],
                            sample['enrolledAt'].iloc[l],
                        ))
            results.extend(duplicate_pairs)

    facilities_processed += 1
    print(f"Finished processing facility: {facility['name']}")

# Create a DataFrame from duplicate results
result_df = pd.DataFrame(results, columns=[
    'facility_name',
    'uid1',
    'uid2',
    'patient_name1',
    'patient_name2',
    'phone_number1',
    'phone_number2',
    'dob1',
    'dob2',
    'age1',
    'age2',
    'similarity_score',
    'enrolledAt1',
    'enrolledAt2'
])

# Sort the DataFrame by facility_name
result_df.sort_values(by='facility_name', inplace=True)

# Export the DataFrame to CSV
result_df.to_csv('duplicate_results_with_dob.csv', index=False)

print("Duplicate detection completed and saved to 'duplicate_results_with_dob.csv'")