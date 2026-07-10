
import pandas as pd
import json
from copy import deepcopy
import re
import zipfile
from io import BytesIO

def run_new_bio_object(df):
    reference = {
        "revision": "09414fdb5747a280b9419ef933eb0f89290b284d",
        "class_identifier": "dut",
        "data": {
            "creation_datetime": "2025-05-20T19:16:34.437849",
            "modification_datetime": "2025-05-20T19:18:14.848630",
            "disable_datetime": None,
            "name": "NCM90-NO-28",
            "basic_characteristics": {
                "nominal_capacity": {"value": 20.485, "display_unit": "milliampere.hour"},
                "nominal_energy": None,
                "nominal_voltage": {"value": 3.4, "display_unit": "volt"},
                "min_voltage": {"value": 1, "display_unit": "volt"},
                "max_voltage": {"value": 5, "display_unit": "volt"},
                "max_charge_current": None,
                "max_discharge_current": None
            },
            "physical_parameters": {
                "mass": {"value": 0.000022761, "display_unit": "gram"},
                "volume": None
            },
            "electrode_parameters": {
                "surface_area": None,
                "characteristic_mass": {"value": 0.00002, "display_unit": "gram"},
                "acquisition_start": {"value": 0, "display_unit": ""},
                "active_material_mass": {"value": 1e-9, "display_unit": "milligram"},
                "active_material_mass_at": {"value": 0, "display_unit": ""},
                "active_material_molecular_weight_at_x0": {"value": 59.318, "display_unit": "gram/mol"},
                "intercalated_ion_molecular_weight_at_x0": {"value": 0.001, "display_unit": "gram/mol"},
                "transfered_electrons_number_per_intercalated_ion": {"value": 1, "display_unit": ""}
            },
            "electrode_information": {
                "electrolyte": "STD",
                "material": "NCM90",
                "other_info": ""
            },
            "id": "dut_690",
            "is_read_only": False,
            "is_default": False,
            "classification": "",
            "producer": "",
            "application": "",
            "supplier": "",
            "manufacturing_datetime": None,
            "tags": ["NCM90-NO-23-28"],
            "author": "user_3",
            "last_editor": "user_3",
            "cloned_from_id": None
        },
        "user_version": "3.0.0-9"
    }

    # Create an in-memory ZIP
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for col in range(df.shape[1]):
            try:
                name = df.iloc[0, col]
                tags = df.iloc[1, col]
                mass = float(df.iloc[2, col])
                nominal_capacity = float(df.iloc[3, col])

                current_ref = deepcopy(reference)
                current_ref["data"]["name"] = name
                current_ref["data"]["tags"] = [tag.strip() for tag in str(tags).split(",")]
                current_ref["data"]["basic_characteristics"]["nominal_capacity"]["value"] = nominal_capacity
                current_ref["data"]["physical_parameters"]["mass"]["value"] = mass

                safe_name = re.sub(r'[\\/*?:"<>|]', "_", name)
                json_string = json.dumps(current_ref, indent=4)

                zipf.writestr(f"{safe_name}.bttest", json_string)
            except Exception as e:
                continue  # Optionally, collect errors and display them later

    zip_buffer.seek(0)
    return zip_buffer, "new_biologic_dut_files.zip"
