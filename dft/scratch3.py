"""
For dealing with smiles vs canonical smiles
"""

from job import *
import molecule as mol
from job_utils import JsonParser
import shutil
import re

from job_manager import JobManager

from config import Config, ConfigKeys

config = Config()


def split_alpha_numeric(s):
    # Use regex to split the string into alphabetical and numerical parts
    match = re.match(r"([a-zA-Z]+)(\d+)", s)
    if match:
        letters, num = match.groups()
        num = int(num) - 1
        return letters, num
    else:
        return None, None


def get_molecule_id(smi):
    m = mol.Molecule(
        smi,
        source=config.get_file(ConfigKeys.MOLECULES)
    )

    return m.id


def scrape_coordinates(path):
    with open(path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if '&zmat' in line:
            start_index = i + 1
            break

    j = start_index
    coord_lines = []
    while '&' not in lines[j]:
        coord_lines.append(lines[j])
        j += 1

    return coord_lines


def get_atom_index_mapping(original_smi, canonical_smi):
    # Create RDKit molecule objects from the SMILES strings
    original_mol = Chem.MolFromSmiles(original_smi)
    canonical_mol = Chem.MolFromSmiles(canonical_smi)

    original_mol = Chem.AddHs(original_mol)
    canonical_mol = Chem.AddHs(canonical_mol)

    # Get the mapping of atom indices from the original molecule to the canonical molecule
    atom_mapping = original_mol.GetSubstructMatch(canonical_mol)

    # Initialize the list with -1 for all indices
    index_mapping = [-1] * original_mol.GetNumAtoms()

    # Fill the index mapping list based on the atom_mapping
    for original_index, canonical_index in enumerate(atom_mapping):
        index_mapping[canonical_index] = original_index

    return index_mapping


def reorder_coordinates_file(smi, path, in_place: bool, new_path=None):
    if in_place:
        new_path = path

    # Scrape coordinates from the file
    coord_lines = scrape_coordinates(path)

    # Assuming the main function passes the correct SMILES string
    original_smi = smi

    # Get the canonical SMILES string
    canonical_smi = Chem.CanonSmiles(original_smi)

    # Get the atom index mapping
    index_mapping = get_atom_index_mapping(original_smi, canonical_smi)

    # Reorder the coordinate lines
    reordered_coords = [None] * len(coord_lines)
    for original_index, canonical_index in enumerate(index_mapping):
        reordered_coords[canonical_index] = coord_lines[original_index]

    # Write the reordered coordinates to the new file
    with open(new_path, 'w') as f:
        # Write the &zmat line
        f.write("&zmat\n")

        # Write the reordered coordinates
        for line in reordered_coords:
            f.write(line)

        # Write the & line, with extra blank line
        f.write("&\n\n")


def main():
    job_manager = JobManager(config.get_file(ConfigKeys.OUT_DIR))

    json_parser = JsonParser(config.get_file(ConfigKeys.MOLECULE_SOURCE))
    unique_molecules = json_parser.get_unique_molecules()

    all_smis = []
    non_canonical_smiles = []
    failed_smis = []
    for category in unique_molecules:
        for smi in unique_molecules[category]:
            try:
                all_smis.append(Chem.CanonSmiles(smi))
                if smi != Chem.CanonSmiles(smi):
                    non_canonical_smiles.append(smi)
            except Exception as e:
                failed_smis.append(smi)

    print(non_canonical_smiles)
    print(len(non_canonical_smiles))
    print()

    # test_smi = '[H]C([C@H](OC(C1=CC=CC=C1)=O)[C@@H]([C@@](COC(C2=CC=CC=C2)=O)(OC(C3=CC=CC=C3)=O)[H])OC(C4=CC=CC=C4)=O)=O'
    #
    # test_canon_mol = Chem.MolFromSmiles(Chem.CanonSmiles(test_smi))
    # test_canon_mol_with_h = Chem.AddHs(test_canon_mol)
    # print(Chem.MolToMolBlock(test_canon_mol_with_h))

    for e, smi in enumerate(non_canonical_smiles):
        mol_id = get_molecule_id(smi)
        path_to_coordinates = os.path.join(config.get_file(ConfigKeys.OUT_DIR), f'J1_{mol_id}_2111', f'J1_{mol_id}_2111.01.in')
        if os.path.exists(path_to_coordinates):
            shutil.copy(path_to_coordinates, os.path.join(config.get_file(ConfigKeys.OUT_DIR), f'J1_{mol_id}_2111', f'COPY_J1_{mol_id}_2111.01.in'))

            reorder_coordinates_file(smi, path_to_coordinates, in_place=True)


if __name__ == "__main__":
    pass
    # main()
