from job import *
import molecule as mol
from typing import List
from job_utils import JsonParser

from rdkit import Chem

json_parser = JsonParser(os.path.join(os_nav.find_project_root(), 'data', 'all_dfs.json'))
unique_molecules = json_parser.get_unique_molecules()

category_to_type = {
    'ald_smiles': mol.MoleculeType.CARBONYL,
    'ylide_smiles': mol.MoleculeType.YLIDE
}

textbook_reactants = []
for category in unique_molecules:
    if 'pdt' not in category:
        textbook_reactants.extend([(category_to_type[category], s) for s in unique_molecules[category]])

df = pd.read_csv(os.path.join(os_nav.find_project_root(), 'data', 'mols', 'vis_df_v2.csv'))
indices = df['index'].tolist()
types = df['type'].tolist()
cas_reactants = df['smiles'].tolist()

cas_canonical = []
for smi in cas_reactants:
    try:
        cas_canonical.append(Chem.MolToSmiles(Chem.MolFromSmiles(smi), isomericSmiles=True))
    except Exception as e:
        cas_canonical.append(smi)
        print(e)
        print(smi)

canon_df = pd.DataFrame({'index': indices, 'type': types, 'smiles': cas_canonical})

print('________________________')

not_found = []
not_found_types = []
for mol_type, smi in textbook_reactants:
    canonicalized_smi = Chem.MolToSmiles(Chem.MolFromSmiles(smi), isomericSmiles=True)
    if canonicalized_smi not in cas_canonical:
        not_found.append((smi, canonicalized_smi))
        not_found_types.append(mol_type.value)

not_found_df = pd.DataFrame({'index': [i + df.shape[0] for i in range(len(not_found))], 'type': not_found_types, 'smiles': [e[1] for e in not_found]})

canon_df = pd.concat([canon_df, not_found_df], ignore_index=True)
canon_df.to_csv(os.path.join(os_nav.find_project_root(), 'data', 'mols', 'wittig_molecules2.csv'), index=False)

for t in not_found:
    print(t)

print()
print(len(not_found))
