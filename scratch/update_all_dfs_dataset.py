import json
from rdkit import Chem
from rdkit.Chem import AllChem

import os
import sys

# Get the current working directory
current_dir = os.getcwd()

# Get the parent directory
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Add the parent directory to the system path
sys.path.insert(0, parent_dir)

import os_navigation as os_nav

cis_wittig_template = '[O:4]=[CH:1].[P:3]=[C:2]>>[C@:2]1[P:3][O:4][C@H:1]1'
trans_wittig_template = '[O:4]=[CH:1].[P:3]=[C:2]>>[C@:2]1[P:3][O:4][C@@H:1]1'

# Function to generate cis and trans products and mapped reactions
def generate_cis_trans_products(ald_smiles, ylide_smiles):
    ald_mol = Chem.MolFromSmiles(ald_smiles)
    ylide_mol = Chem.MolFromSmiles(ylide_smiles)

    cis_reaction = AllChem.ReactionFromSmarts(cis_wittig_template)
    trans_reaction = AllChem.ReactionFromSmarts(trans_wittig_template)

    cis_pdt = cis_reaction.RunReactants((ald_mol, ylide_mol))[0][0]
    trans_pdt = trans_reaction.RunReactants((ald_mol, ylide_mol))[0][0]

    cis_pdt_smiles = Chem.MolToSmiles(cis_pdt)
    trans_pdt_smiles = Chem.MolToSmiles(trans_pdt)

    return cis_pdt_smiles, trans_pdt_smiles

# Load the JSON data
file_path = os.path.join(os_nav.find_project_root(), 'data', 'all_dfs.json')
with open(file_path, 'r') as file:
    data = json.load(file)

# Generate cis and trans products for missing entries and update the data
for entry in data:
    if entry['cis_pdt'] is None or entry['trans_pdt'] is None:
        ald_smiles = entry['ald_smiles']
        ylide_smiles = entry['ylide_smiles']
        cis_pdt, trans_pdt = generate_cis_trans_products(ald_smiles, ylide_smiles)
        entry['cis_pdt'] = cis_pdt
        entry['trans_pdt'] = trans_pdt

        # Update mapped reactions as well
        entry['cis_mapped_rxn'] = cis_wittig_template
        entry['trans_mapped_rxn'] = trans_wittig_template

# Save the updated data back to a JSON file
updated_file_path = os.path.join(os_nav.find_project_root(), 'data', 'all_dfs.json')
with open(updated_file_path, 'w') as file:
    json.dump(data, file, indent=2)

print(f"Updated data saved to {updated_file_path}")
