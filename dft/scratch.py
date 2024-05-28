from job import *
import molecule as mol
from typing import List
from job_utils import JsonParser

from rdkit import Chem

json_parser = JsonParser(os.path.join(os_nav.find_project_root(), 'data', 'all_dfs.json'))
unique_molecules = json_parser.get_unique_molecules()

textbook_reactants = []
for category in unique_molecules:
    if 'pdt' not in category:
        textbook_reactants.extend(unique_molecules[category])

df = pd.read_csv(os.path.join(os_nav.find_project_root(), 'data', 'mols', 'wittig_reactants.csv'))
indices = df['index'].tolist()
cas_reactants = df['reactant_smiles'].tolist()

cas_canonical = []
for smi in cas_reactants:
    try:
        cas_canonical.append(Chem.MolToSmiles(Chem.MolFromSmiles(smi), isomericSmiles=True))
    except Exception as e:
        cas_canonical.append(smi)
        print(e)
        print(smi)

canon_df = pd.DataFrame({'index': indices, 'reactant_smiles': cas_canonical})

print('________________________')

not_found = []
for smi in textbook_reactants:
    canonicalized_smi = Chem.MolToSmiles(Chem.MolFromSmiles(smi), isomericSmiles=True)
    if canonicalized_smi not in cas_canonical:
        not_found.append((smi, canonicalized_smi))

not_found_df = pd.DataFrame({'index': [i + df.shape[0] for i in range(len(not_found))], 'reactant_smiles': [e[1] for e in not_found]})

canon_df = pd.concat([canon_df, not_found_df], ignore_index=True)
canon_df.to_csv(os.path.join(os_nav.find_project_root(), 'data', 'mols', 'wittig_reactants.csv'), index=False)

for t in not_found:
    print(t)

print()
print(len(not_found))
