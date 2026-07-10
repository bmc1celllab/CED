import pandas as pd
from io import BytesIO
import zipfile

def run(df_raw, component_name='cathode'):
    """
    df_raw: DataFrame where the first row is mass values, columns are sample names
    component_name: 'cathode' or 'anode'
    Returns: (zip_buffer, zip_filename)
    """
    # First row is data, so reassign headers
    df = df_raw.copy()
    df.columns = df.iloc[0]         # Set first row as header
    df = df[1:].reset_index(drop=True)  # Drop first row, reset index

    sample_names = df.columns.tolist()

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for sample in sample_names:
            col_data = df[sample].dropna().astype(float)

            for idx, mass in enumerate(col_data, start=1):
                filename = f"{sample}-{idx}.TO"

                lines = [
                    '[Content]\n',
                    'm_bAutoCalcNCapacity=1\n',
                    f'm_fMass={mass}\n',
                    'm_fMaxCurrentCharge=0.2\n',
                    'm_fMaxVoltageCharge=5\n',
                    'm_fMinVoltageCharge=-1\n',
                    'm_fNorminalCapacitor=0\n',
                    'm_fNorminalCapacity=0\n',
                    'm_fNorminalIR=0\n',
                    'm_fNorminalVoltage=0\n',
                ]

                if component_name.lower() == 'cathode':
                    lines.append('m_fSpecificCapacity=0.17\n')
                else:
                    lines.append('m_fSpecificCapacity=0.360\n')

                lines += [
                    'SER=1321994960\n',
                    'VER=27265537\n'
                ]

                zipf.writestr(filename, ''.join(lines))

    zip_buffer.seek(0)
    return zip_buffer, f"{component_name}_object_files.zip"
