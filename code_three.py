import pandas as pd
from io import BytesIO
import zipfile
import os

def run(df, template_text=None):
    if template_text is None:
        with open("reference", "r", encoding="latin-1") as f:
            template_text = f.read()
    """
    Converts Excel data (OB sheet) into .mps files based on a text template.
    Returns (zip_buffer, zip_filename)
    """

    # Field mappings from Excel row index → MPS label
    fields = {
        0: ("Filename", ""),
        1: ("Electrode material", ""),
        2: ("Characteristic mass", " g"),
        3: ("Battery capacity", " mA.h")
    }

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for col in df.columns:
            lines = template_text.splitlines()
            replacements = {}

            for row, (label, unit) in fields.items():
                val = str(df.iloc[row, col]).strip()
                if unit and not val.endswith(unit):
                    val += unit
                replacements[label] = f"{label} : {val}"

            # Apply replacements to the template
            new_lines = []
            for line in lines:
                replaced = False
                for label, new_line in replacements.items():
                    if line.strip().startswith(label):
                        new_lines.append(new_line)
                        replaced = True
                        break
                if not replaced:
                    new_lines.append(line)

            filename = str(df.iloc[0, col]).replace(" ", "_") + ".mps"
            file_content = "\n".join(new_lines)
            zipf.writestr(filename, file_content)

    zip_buffer.seek(0)
    return zip_buffer, "old_biologic_mps_files.zip"
