import os
import pandas as pd
import json
from pprint import pprint

import dft.molecule as mol

# Define the path to the JSON file
PATH = '/Users/lucasabounader/PycharmProjects/active_learner/saved_files/vis_df_v2.json'
output_csv_path = '/data/mols/vis_df_v2.csv'

with open(PATH, 'r') as file:
    data = json.load(file)

mol_type_dict = {
    'carbonyl': mol.MoleculeType.CARBONYL,
    'alkyl': mol.MoleculeType.YLIDE,
    'phosphine': mol.MoleculeType.PHOSPHINE
}

# Convert the JSON structure to a pandas DataFrame
df = pd.DataFrame(data)

# Map the reactant_type to its corresponding MoleculeType value
df['type'] = df['reactant_type'].map(lambda x: mol_type_dict[x].value)

# Select the required columns and rename them
df = df[['type', 'reactant_smiles']].reset_index()
df.rename(columns={'reactant_smiles': 'smiles'}, inplace=True)

# Export the DataFrame to a CSV file
df.to_csv(output_csv_path, index=False)

print(f"CSV file saved to: {output_csv_path}")
