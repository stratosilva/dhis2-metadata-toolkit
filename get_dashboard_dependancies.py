import csv
import re
from dhis2 import logger, setup_logger, RequestException

import time

from dhis2_env import get_api

# Configura tu instancia DHIS2. Las credenciales vienen de .env (ver .env.example).
api = get_api("EPHI_STAGING")

# Lista de program rule IDs que quieres eliminar
# program_rule_ids = [
#     "LYxsRYMD0mu", "dK4E4bJmo4c", "gkpWJodauGq", "xT04CQK3S2U", "OLS8lrcuEEG",
#     "HmnP1nhVqFA", "OjzLCiY0FtX", "xxu23hHiLk6", "urP4v63uQOD", "O03VAO1MJts",
#     "N3NGOgyoHdV", "HgKp9ePVfyl", "EgC7EGNhhIg", "RN7vc7gg4ho", "NAge7fSU6P1",
#     "V5gBvAEnYBS", "qgFG59n2406", "V3ThNsqnnPP", "hefg3Ne42vD", "TPRzg4CcRuE",
#     "HsD4lS0URV0", "eJmpNSXkhuw", "JT9zc87399c", "am81NXc7NWB", "DnHTMZ3TpXA",
#     "pWCJp8e2Yqd", "lFqmheHTMDx", "qczuGx6g4Fm", "BeKcRyzlCh8", "qwtvHylgMlk",
#     "SkuHEQSZ5mF", "fMKYCOGUIIr", "uQUWf4kmVLB", "eg1F5xz7tOq", "Nxrz7dJpMsa",
#     "Uh1WNRpo01r", "xKWwdNGaoC3", "jSwh6U4jmHB", "JCRfroEmXp2", "Zd9MLJ7eqEG",
#     "gndvqZkoD76", "RbaukyKohHK", "kWqbLa022Ar", "VSPIDmsS0VX", "ihYA3mWR57D",
#     "CmvUSCHqjxh", "QSrtaj07Na0", "RXSmGyqaAtU", "TT2VNweW1RL", "BladD3rvW5S",
#     "BUpaTXuzt8w", "Iia0RIqbHMd", "Qgyv7OXwRod", "c3QyCZrgsuV", "KiKd9OUCc6X",
#     "C5VxZBZYkb6", "hdMEFzj4jsJ", "C8zKDt6gR6S", "sTvk0km8jui", "LOlhFMxzXs4",
#     "JWnyQKk3G2z", "foeiZjpG33H", "bJrfAOaCq2G", "vpfnDuxWPqe", "xiWDyGLSrIN",
#     "tmrmaI9O2yr", "JDOQ9zqhLOR", "VeFiKcQEXqi", "USdZy9KujkQ", "wAVslLMaigU",
#     "Et8vkhhvZyT", "mRw7qSr8GKC", "oS2cJf1Wss2", "RVyz1e6miwp", "OiipYkIFkjT",
#     "uT3hHhP1Smk", "HOtSiLZ8cw0", "Xs8PNXIy4yg", "L57rMO4vQjl", "PwwPLEBcYrz",
#     "PPJYqKOMUqk", "w2uHVdM9FUw", "lkhQ69HoFMT", "cyOih2YSH2R", "bViAhZDSRfW",
#     "F98z9aWeYn7", "b2q2UhpaT6y", "LYzypmRlQCf", "MVBcYH1qAOu", "x3Kmul5Nkzk",
#     "Pk0o3u7demQ", "r30UOIYoDt9", "XkYiNgzsa0O", "iOxj6Fv4qhE", "XGA66pknOCI",
#     "mzTZBEl1JnH", "QKlU7zaXEzR", "hv9IupHJPID", "sbcjdtm90aA", "Z8d2yntAWb9",
#     "PorslHBwO97", "zADzIdH0q38", "AnOv6Mw93v8", "IYP541pdTRG"
# ]
#
# # Paso 1: Eliminar todas las Program Rule Actions asociadas
# for pr_id in program_rule_ids:
#     try:
#         # Buscar acciones asociadas
#         actions = api.get(f"programRuleActions?filter=programRule.id:eq:{pr_id}").json()
#         for action in actions.get("programRuleActions", []):
#             action_id = action["id"]
#             print(f"Deleting ProgramRuleAction {action_id}")
#             api.delete(f"programRuleActions/{action_id}")
#             time.sleep(0.1)
#     except Exception as e:
#         print(f"Error deleting actions for {pr_id}: {e}")
#
# # Paso 2: Eliminar las Program Rules
# for pr_id in program_rule_ids:
#     try:
#         print(f"Deleting ProgramRule {pr_id}")
#         api.delete(f"programRules/{pr_id}")
#         time.sleep(0.1)
#     except Exception as e:
#         print(f"Error deleting rule {pr_id}: {e}")
#
# exit(0)

import csv
import json
import re
from requests.exceptions import RequestException

# --- assume you already have these available in your codebase ---
# from your_api_wrapper import Api
# from your_logging_setup import setup_logger, logger

DEFAULT_CATEGORY_COMBO_UID = "bjDvmb4bfuf"


def get_dashboard_details(api, dashboard_id):
    logger.info(f"Fetching dashboard details for ID: {dashboard_id}")
    return api.get(f"dashboards/{dashboard_id}",
                   params={"fields": "id,name,dashboardItems[id,type,visualization[id]]"}).json()


def get_visualization_details(api, visualization_id):
    logger.info(f"Fetching visualization details for ID: {visualization_id}")
    return api.get(f"visualizations/{visualization_id}", params={"fields": ":owner,dataDimensionItems[*]"}).json()


def get_name_by_type_and_id(api, type_, id_):
    try:
        return api.get(f"{type_}/{id_}", params={"fields": "name"}).json().get("name", "Unknown")
    except:
        return "Unknown"


def get_program_indicator(api, data_element_id):
    response = api.get(
        "programIndicators",
        params={"fields": "id,name", "filter": f"attributeValues.value:eq:{data_element_id}"}
    ).json()
    if response.get("programIndicators"):
        pi = response["programIndicators"][0]
        return pi.get("id"), pi.get("name")
    return None, None


def get_indicator_details(api, indicator_id):
    return api.get(f"indicators/{indicator_id}", params={"fields": ":owner,numerator,denominator"}).json()


def get_data_element_details(api, de_id):
    return api.get(f"dataElements/{de_id}", params={"fields": ":owner,categoryCombo"}).json()


def get_program_indicator_details(api, pi_id):
    return api.get(f"programIndicators/{pi_id}", params={"fields": ":owner"}).json()


def get_category_combo_dependency_map(api, cc_id):
    return api.get(
        f"categoryCombos/{cc_id}",
        params={"fields": "id,categories[id,categoryOptions[id]],categoryOptionCombos[id]"}
    ).json()


def get_metadata_object(api, endpoint, uid):
    return api.get(f"{endpoint}/{uid}", params={"fields": ":owner"}).json()


def extract_uids_from_expression(expression, prefix):
    if prefix == "#":
        pattern = r"#\{([a-zA-Z0-9]{11})\}"
    elif prefix == "I":
        pattern = r"I\{([a-zA-Z0-9]{11})\}"
    else:
        return []
    return list(set(re.findall(pattern, expression or "")))


def collect_category_combo_dependencies(api, de_full, bundle, seen_sets):
    cc = de_full.get("categoryCombo") or {}
    cc_id = cc.get("id")

    if not cc_id or cc_id == DEFAULT_CATEGORY_COMBO_UID:
        return

    if cc_id not in seen_sets['categoryCombos']:
        cc_map = get_category_combo_dependency_map(api, cc_id)

        cc_full = get_metadata_object(api, "categoryCombos", cc_id)
        seen_sets['categoryCombos'].add(cc_id)
        bundle["categoryCombos"].append(cc_full)

        for category in cc_map.get("categories", []):
            cat_id = category.get("id")
            if cat_id and cat_id not in seen_sets['categories']:
                bundle["categories"].append(get_metadata_object(api, "categories", cat_id))
                seen_sets['categories'].add(cat_id)

            for co in category.get("categoryOptions", []):
                co_id = co.get("id")
                if co_id and co_id not in seen_sets['categoryOptions']:
                    bundle["categoryOptions"].append(get_metadata_object(api, "categoryOptions", co_id))
                    seen_sets['categoryOptions'].add(co_id)

        for coc in cc_map.get("categoryOptionCombos", []):
            coc_id = coc.get("id")
            if coc_id and coc_id not in seen_sets['categoryOptionCombos']:
                bundle["categoryOptionCombos"].append(get_metadata_object(api, "categoryOptionCombos", coc_id))
                seen_sets['categoryOptionCombos'].add(coc_id)


def main():
    # Setup logger
    setup_logger()

    # Connect to API. Credentials come from .env (see .env.example); switch
    # instances by changing the prefix, e.g. "NG_NCD_ANALYST".
    try:
        api = get_api("SIMPLE_SANDBOX")
        logger.info("Connected to DHIS2 API")
    except RequestException as e:
        logger.error(f"Failed to connect to DHIS2 API: {e}")
        return

    # Fetch dashboard details (full object for import)
    DASHBOARD_ID = "iJBj2gsAuN7"

    # 1. Initialize Bundle and Tracking Sets
    bundle = {
        "dashboards": [], "visualizations": [], "indicators": [],
        "dataElements": [], "programIndicators": [], "categoryCombos": [],
        "categoryOptionCombos": [], "categories": [], "categoryOptions": []
    }

    seen = {
        "dashboards": set(), "visualizations": set(), "indicators": set(),
        "dataElements": set(), "programIndicators": set(), "categoryCombos": set(),
        "categoryOptionCombos": set(), "categories": set(), "categoryOptions": set()
    }

    # 2. Fetch Dashboard
    dashboard_details = get_dashboard_details(api, DASHBOARD_ID)
    bundle["dashboards"].append(dashboard_details)
    seen["dashboards"].add(DASHBOARD_ID)

    # 3. Process Items for CSV and JSON
    output_csv = "dashboard_items.csv"

    with open(output_csv, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "item_type", "viz_id", "viz_name", "data_type", "data_id", "data_name", "pi_id", "pi_name"
        ])

        for item in dashboard_details.get("dashboardItems", []):
            if item.get("type") != "VISUALIZATION":
                continue

            viz_ref = item.get("visualization") or {}
            viz_id = viz_ref.get("id")
            if not viz_id: continue

            # Fetch fresh details for dependencies
            viz_full = get_visualization_details(api, viz_id)
            viz_name = viz_full.get("name", "Unnamed")

            if viz_id not in seen["visualizations"]:
                bundle["visualizations"].append(viz_full)
                seen["visualizations"].add(viz_id)

            for ddi in viz_full.get("dataDimensionItems", []):
                dtype = ddi.get("dataDimensionItemType")
                did, dname, pi_id, pi_name = None, None, None, None

                # Handle Standard Items and Operands (DE.COC)
                if dtype == "DATA_ELEMENT":
                    did = ddi.get("dataElement", {}).get("id")
                elif dtype == "INDICATOR":
                    did = ddi.get("indicator", {}).get("id")
                elif dtype == "PROGRAM_INDICATOR":
                    did = ddi.get("programIndicator", {}).get("id")
                elif dtype == "DATA_ELEMENT_OPERAND":
                    # Extract from nested operand object in your payload
                    deo = ddi.get("dataElementOperand", {})
                    did = deo.get("dataElement", {}).get("id")
                    # Track COC if it exists
                    coc_id = deo.get("categoryOptionCombo", {}).get("id")
                    if coc_id and coc_id not in seen["categoryOptionCombos"]:
                        bundle["categoryOptionCombos"].append(get_metadata_object(api, "categoryOptionCombos", coc_id))
                        seen["categoryOptionCombos"].add(coc_id)

                if not did: continue

                # Resolve Names and Dependencies
                if dtype in ["DATA_ELEMENT", "DATA_ELEMENT_OPERAND"]:
                    dname = get_name_by_type_and_id(api, "dataElements", did)
                    pi_id, pi_name = get_program_indicator(api, did)
                    if did not in seen["dataElements"]:
                        de_obj = get_data_element_details(api, did)
                        bundle["dataElements"].append(de_obj)
                        seen["dataElements"].add(did)
                        collect_category_combo_dependencies(api, de_obj, bundle, seen)

                elif dtype == "INDICATOR":
                    dname = get_name_by_type_and_id(api, "indicators", did)
                    if did not in seen["indicators"]:
                        ind_obj = get_indicator_details(api, did)
                        bundle["indicators"].append(ind_obj)
                        seen["indicators"].add(did)
                        # Parse nested expressions
                        for field in ["numerator", "denominator"]:
                            expr = ind_obj.get(field, "")
                            for sub_de in extract_uids_from_expression(expr, "#"):
                                if sub_de not in seen["dataElements"]:
                                    sub_de_obj = get_data_element_details(api, sub_de)
                                    bundle["dataElements"].append(sub_de_obj)
                                    seen["dataElements"].add(sub_de)
                                    collect_category_combo_dependencies(api, sub_de_obj, bundle, seen)
                            for sub_pi in extract_uids_from_expression(expr, "I"):
                                if sub_pi not in seen["programIndicators"]:
                                    bundle["programIndicators"].append(get_program_indicator_details(api, sub_pi))
                                    seen["programIndicators"].add(sub_pi)

                elif dtype == "PROGRAM_INDICATOR":
                    dname = get_name_by_type_and_id(api, "programIndicators", did)
                    pi_id, pi_name = did, dname
                    if did not in seen["programIndicators"]:
                        bundle["programIndicators"].append(get_program_indicator_details(api, did))
                        seen["programIndicators"].add(did)

                # Write row to CSV
                writer.writerow(["VISUALIZATION", viz_id, viz_name, dtype, did, dname, pi_id, pi_name])

    # 4. Save JSON Bundle
    with open("dashboard_bundle.json", "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)

    logger.info(f"Done. CSV saved to {output_csv}, JSON bundle saved to dashboard_bundle.json")


if __name__ == "__main__":
    main()