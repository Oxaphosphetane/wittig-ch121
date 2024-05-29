import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Draw, AllChem, rdFMCS
import sys
import os
import enum

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)
import os_navigation as os_nav

from html_templates import Visualize3DHtml

# Disable all RDKit warnings
from rdkit import RDLogger

logger = RDLogger.logger()
logger.setLevel(RDLogger.ERROR)  # Show only errors, no warnings


# Alternatively, to completely turn off logging including errors, use:
# logger.setLevel(RDLogger.CRITICAL)


class _ForceFieldMethod:
    UFF = 'uff'
    MMFF = 'mmff'


class MoleculeType(enum.Enum):
    UNCATEGORIZED = 'UNCATEGORIZED'
    OXAPHOSPHETANE = 'OXAPHOSPHETANE'
    CARBONYL = 'CARBONYL'
    YLIDE = 'YLIDE'
    SOLVENT = 'SOLVENT'
    ADDITIVE = 'ADDITIVE'
    PHOSPHINE = 'PHOSPHINE'


class Molecule:
    def __init__(
            self,
            smiles: str,
            source: str = os.path.join(os_nav.find_project_root(), 'data', 'mols', 'uncategorized.csv'),
            type: MoleculeType = MoleculeType.UNCATEGORIZED
    ):
        self.molecule = Chem.MolFromSmiles(smiles)
        if self.molecule is None:
            raise ValueError("Invalid SMILES string provided")
        self.molecule_with_hydrogens = Chem.AddHs(self.molecule)
        self.canonical_smiles = Chem.MolToSmiles(self.molecule, isomericSmiles=True)
        self.source = source
        self.type = type
        self.id = self._generate_id()

    @classmethod
    def from_rdkit_mol(cls, mol, source: str = os.path.join(os_nav.find_project_root(), 'data', 'mols', 'uncategorized.csv')):
        smi = Chem.MolToSmiles(mol, isomericSmiles=True)
        m = cls(smi, source=source)
        m.molecule = mol
        m.molecule_with_hydrogens = Chem.AddHs(mol)
        return m

    def get_formula(self):
        return rdMolDescriptors.CalcMolFormula(self.molecule_with_hydrogens)

    def num_atoms(self):
        return self.molecule_with_hydrogens.GetNumAtoms()

    def visualize(self):
        img = Draw.MolToImage(self.molecule_with_hydrogens)
        img.save("molecule.png")

    def embed_3d(self, max_attempts=3) -> bool:
        params = AllChem.ETKDGv3()
        params.numThreads = 0
        for attempt in range(max_attempts):
            params.randomSeed = 42 + attempt
            status = AllChem.EmbedMolecule(self.molecule_with_hydrogens, params)
            if status == 0:
                return True
        return False

    def optimize_3d(self, force_field=_ForceFieldMethod.UFF, constrain=False):
        if force_field == _ForceFieldMethod.UFF:
            ff = AllChem.UFFGetMoleculeForceField(self.molecule_with_hydrogens)
        elif force_field == _ForceFieldMethod.MMFF:
            ff = AllChem.MMFFGetMoleculeForceField(self.molecule_with_hydrogens,
                                                   AllChem.MMFFGetMoleculeProperties(self.molecule_with_hydrogens))
        else:
            raise ValueError("Unsupported force field. Choose 'uff' or 'mmff'.")

        if ff is not None:
            ff.Minimize(500)
        else:
            raise Exception("Failed to create force field for optimization.")

    def generate_3d_coordinates(self, optimize=True, force_field=_ForceFieldMethod.UFF, constrain_opt=False):
        if self.embed_3d():  # modifies Molecule in place and returns bool True if success
            if optimize:
                self.optimize_3d(force_field, constrain=constrain_opt)
        else:
            raise Exception("Failed to embed molecule, cannot proceed with optimization.")

        return Chem.MolToMolBlock(self.molecule_with_hydrogens)

    def export_conformer_coordinates(self, conf_id=0, idx_start=1):
        """
        Export the 3D coordinates of a conformer in a specified format.

        :param conf_id: The ID of the conformer to export (default is 0).
        :return: A string with the coordinates in the specified format.
        """
        self.generate_3d_coordinates()

        mol = self.molecule_with_hydrogens

        conf = mol.GetConformer(conf_id)
        lines = []

        for atom in mol.GetAtoms():
            pos = conf.GetAtomPosition(atom.GetIdx())
            symbol = atom.GetSymbol()
            idx = atom.GetIdx() + idx_start  # add Atom index start
            line = f"{symbol}{idx:<2} {pos.x:>20.10f} {pos.y:>20.10f} {pos.z:>20.10f}"
            lines.append(line)

        return "\n".join(lines)

    def visualize_3d(self, label='') -> str:
        mb = Chem.MolToMolBlock(self.molecule_with_hydrogens)
        mb_escaped = mb.replace('\n', '\\n').replace('\'', '\\\'').replace('\"', '\\"')
        html = Visualize3DHtml(mb_escaped).raw_html
        with open(f'molecule_visualization_test_{label}.html', 'w') as f:
            f.write(html)
        print(
            "3D visualization written to 'molecule_visualization_test.html'. Open this file in a web browser to view the molecule.")
        return html

    def get_canonical_smiles(self):
        return self.canonical_smiles

    def _generate_id(self):
        df = pd.read_csv(self.source)
        if self.canonical_smiles in df['smiles'].values:
            matching_row = df[df['smiles'] == self.canonical_smiles]
            return matching_row.index[0]

        # Generate a new ID
        new_id = df.index.max() + 1 if not df.empty else 0

        # Create new row to append
        new_row = {
            'index': new_id,
            'type': self.type.value,
            'smiles': self.canonical_smiles,
        }

        # Set other columns to None or a specific marker
        for col in df.columns:
            if col not in new_row:
                new_row[col] = None

        # Append the new row to the DataFrame using concat
        df = pd.concat([df, pd.DataFrame([new_row], index=[new_id])])

        # Save the updated DataFrame back to the CSV file
        df.to_csv(self.source, index=False)

        return new_id


class OxaphosEmbedParams:
    """Create 3D embedding parameters for an Oxaphosphetane."""
    cis_pph3_sdf_idxs = [0, 1]
    trans_pph3_sdf_idxs = [2, 3]
    cis_chop_sdf_idxs = [4, 5]
    trans_chop_sdf_idxs = [6, 7]

    path_to_templates = os.path.join(os_nav.find_project_root(), 'data')

    core_ring_smiles = 'C1COP1'
    core_ring_pph3_smiles = 'C1COP1(c1ccccc1)(c1ccccc1)c1ccccc1'

    extract_phosphine_smirks = "C1COP1([*:1])([*:2])[*:3]>>P([*:1])([*:2])[*:3]"

    def __init__(
            self,
            oxaphos_mol: Chem.Mol,
            is_triphenyl=True,
            is_cis=True,
            ligand_atoms: tuple = None,
            chain_atoms: tuple = None,
    ):
        self.sdf_reader = Chem.SDMolSupplier(os.path.join(OxaphosEmbedParams.path_to_templates, 'OP_templates.sdf'),
                                             removeHs=False)
        self.template_mol = self.get_template_mol(oxaphos_mol, is_triphenyl, is_cis, ligand_atoms, chain_atoms)

    @staticmethod
    def get_ring_indices(mol) -> tuple:
        """Return oxaphosphetane ring indices in format (c1_idx, c2_idx, o_idx, p_idx)."""
        ring_template = Chem.MolFromSmiles(OxaphosEmbedParams.core_ring_smiles)
        matches = mol.GetSubstructMatches(ring_template)

        try:
            return matches[0]
        except IndexError:
            raise Exception("Molecule is not an oxaphosphetane.")

    @staticmethod
    def find_chain_leads(mol) -> tuple:
        ring_indices = OxaphosEmbedParams.get_ring_indices(mol)
        c1_idx, c2_idx = ring_indices[0], ring_indices[1]

        c1_atom = mol.GetAtomWithIdx(c1_idx)
        c2_atom = mol.GetAtomWithIdx(c2_idx)

        def find_chain(ring_atom):
            neighbors = ring_atom.GetNeighbors()
            for neighbor in neighbors:
                if neighbor.GetIdx() not in ring_indices and neighbor.GetSymbol() != 'H':
                    return neighbor

        return tuple(map(find_chain, (c1_atom, c2_atom)))

    @staticmethod
    def find_ligand_leads(mol) -> tuple:
        ring_indices = OxaphosEmbedParams.get_ring_indices(mol)
        p_idx = ring_indices[3]
        p_atom = mol.GetAtomWithIdx(p_idx)

        neighbors = [nb for nb in p_atom.GetNeighbors() if nb.GetIdx() not in ring_indices]

        return tuple(neighbors)

    @staticmethod
    def replace_atom(mol, atom_index, new_atomic_num):
        """Replace an atom in a molecule with another atom of a different type."""
        rw_mol = Chem.RWMol(mol)  # Create an editable molecule from the original molecule
        rw_mol.ReplaceAtom(atom_index, Chem.Atom(
            new_atomic_num))  # Replace the specified atom with a new atom of the specified type
        new_mol = rw_mol.GetMol()  # Get a new molecule from the editable molecule
        Chem.SanitizeMol(new_mol)  # Important to update the molecule's properties

        return new_mol

    @staticmethod
    def update_chain_atoms(mol, chain_atoms: tuple):
        chain_atoms = OxaphosEmbedParams.find_chain_leads(mol)

        non_carbon_atoms = [atom for atom in chain_atoms if atom.GetSymbol() != 'C']
        for (i, atom) in enumerate(non_carbon_atoms):
            mol = OxaphosEmbedParams.replace_atom(mol, chain_atoms[i], atom.GetAtomicNum())

        return mol

    @staticmethod
    def update_ligand_atoms(mol, ligand_atoms: tuple):
        ligand_atoms = OxaphosEmbedParams.find_ligand_leads(mol)

        non_carbon_atoms = [atom for atom in ligand_atoms if atom.GetSymbol() != 'C']
        for (i, atom) in enumerate(non_carbon_atoms):
            mol = OxaphosEmbedParams.replace_atom(mol, ligand_atoms[i].GetIdx(), atom.GetAtomicNum())

        return mol

    def get_template_mol(self, target_mol, is_triphenyl, is_cis, ligand_atoms, chain_atoms):
        if is_triphenyl and is_cis:
            idxs = OxaphosEmbedParams.cis_pph3_sdf_idxs
        elif is_triphenyl and not is_cis:
            idxs = OxaphosEmbedParams.trans_pph3_sdf_idxs
        elif not is_triphenyl and is_cis:
            idxs = OxaphosEmbedParams.cis_chop_sdf_idxs
        else:
            idxs = OxaphosEmbedParams.trans_chop_sdf_idxs

        template_mol = None  # initialize
        for i in idxs:  # find proper enantiomers
            prelim_template_mol = self.sdf_reader[i]

            if chain_atoms is not None:
                prelim_template_mol = OxaphosEmbedParams.update_chain_atoms(prelim_template_mol, chain_atoms)
            if ligand_atoms is not None:
                prelim_template_mol = OxaphosEmbedParams.update_ligand_atoms(prelim_template_mol, ligand_atoms)

            if target_mol.HasSubstructMatch(Chem.RemoveAllHs(prelim_template_mol), useChirality=True):
                template_mol = prelim_template_mol

        if template_mol is None:
            raise Exception("Something doesn't add up: Check is_triphenyl and is_cis and try again.")

        return template_mol


class Oxaphosphetane(Molecule):
    def __init__(
            self,
            smiles: str,
            source: str = os.path.join(os_nav.find_project_root(), 'data', 'mols', 'wittig_molecules.csv'),
            type: MoleculeType = MoleculeType.OXAPHOSPHETANE
    ):
        super().__init__(smiles, source=source, type=type)
        self.ring_indices = OxaphosEmbedParams.get_ring_indices(self.molecule_with_hydrogens)
        self.cis_templates = self.make_cis_templates()
        self.constraint_core_mol = OxaphosEmbedParams(
            oxaphos_mol=self.molecule_with_hydrogens,
            is_triphenyl=self.is_triphenyl(),
            is_cis=self.is_cis(),
            ligand_atoms=OxaphosEmbedParams.find_ligand_leads(self.molecule_with_hydrogens),
            chain_atoms=OxaphosEmbedParams.find_chain_leads(self.molecule_with_hydrogens)
        ).template_mol

    def find_chain_leads(self) -> tuple:
        c1_idx, c2_idx = self.ring_indices[0], self.ring_indices[1]

        c1_atom = self.molecule_with_hydrogens.GetAtomWithIdx(c1_idx)
        c2_atom = self.molecule_with_hydrogens.GetAtomWithIdx(c2_idx)

        def find_chain(ring_atom):
            neighbors = ring_atom.GetNeighbors()
            for neighbor in neighbors:
                if neighbor.GetIdx() not in self.ring_indices and neighbor.GetSymbol() != 'H':
                    return neighbor

        return tuple(map(find_chain, (c1_atom, c2_atom)))

    def find_ligand_leads(self) -> tuple:
        p_idx = self.ring_indices[3]
        p_atom = self.molecule_with_hydrogens.GetAtomWithIdx(p_idx)

        neighbors = [nb for nb in p_atom.GetNeighbors() if nb.GetIdx() not in self.ring_indices]

        return tuple(neighbors)

    def make_cis_templates(self) -> str:
        nb1, nb2 = self.find_chain_leads()
        R1, R2 = nb1.GetSymbol(), nb2.GetSymbol()

        return f"{R1}[C@H]1[C@@H]({R2})OP1", f"{R1}[C@@H]1[C@H]({R2})OP1"

    def make_trans_templates(self) -> str:
        R1, R2 = self.find_chain_leads()

        return f"{R1}[C@H]1[C@H]({R2})OP1", f"{R1}[C@@H]1[C@@H]({R2})OP1"

    def is_cis(self) -> bool:
        """Checks if a molecule is cis-disubstituted."""
        # Perform the substructure search with stereochemistry consideration
        for template in self.make_cis_templates():
            if self.molecule_with_hydrogens.HasSubstructMatch(Chem.MolFromSmiles(template), useChirality=True):
                return True

        return False

    def is_trans(self) -> bool:
        """Checks if a molecule is trans-disubstituted."""
        for template in self.make_trans_templates():
            if self.molecule_with_hydrogens.HasSubstructMatch(Chem.MolFromSmiles(template), useChirality=True):
                return True

        return False

    def is_triphenyl(self) -> bool:
        """Checks if the Oxaphosphetane is derived from a triphenyl phosphine."""
        triphenyl_ring_template = Chem.MolFromSmiles(OxaphosEmbedParams.core_ring_pph3_smiles)

        transform = AllChem.ReactionFromSmarts(OxaphosEmbedParams.extract_phosphine_smirks)

        products = transform.RunReactants((AllChem.RemoveAllHs(self.molecule),))

        phosphine = products[0][0]

        if phosphine.HasSubstructMatch(triphenyl_ring_template) and triphenyl_ring_template.hasSubstructMatch(
                phosphine):
            return True

        return False

    def embed_3d(self, max_attempts=10) -> bool:
        # Perform the constrained embedding
        try:
            # Attempt to match the core coordinates and constrain the embedding
            cid = AllChem.ConstrainedEmbed(self.molecule_with_hydrogens, Chem.RemoveAllHs(self.constraint_core_mol))
            print("Constrained embedding successful, conformation ID:", cid)
            return True
        except ValueError as e:
            print("Constrained embedding failed:", e)
            return False

    def optimize_3d(self, force_field=_ForceFieldMethod.MMFF, constrain=False):
        # Set up the force field
        if force_field == _ForceFieldMethod.UFF:
            ff = AllChem.UFFGetMoleculeForceField(self.molecule_with_hydrogens)
        elif force_field == _ForceFieldMethod.MMFF:
            ff = AllChem.MMFFGetMoleculeForceField(self.molecule_with_hydrogens,
                                                   AllChem.MMFFGetMoleculeProperties(self.molecule_with_hydrogens))
        else:
            raise ValueError("Unsupported force field. Choose 'uff' or 'mmff'.")

        if ff is None:
            raise Exception("Failed to create force field for optimization.")

        if constrain:
            # Find the matching substructure to apply constraints
            match = self.molecule_with_hydrogens.GetSubstructMatch(Chem.RemoveAllHs(self.constraint_core_mol))
            if not match:
                raise Exception("Core coordinates not found in the molecule.")
            # Apply constraints to the matched core atoms
            for idx in match:
                ff.AddFixedPoint(idx)

        # Perform the optimization
        ff.Minimize(500)
        print("Optimization with constrained core successful.")


test_file = False
if test_file:
    # Example usage:
    try:
        # oxaphos = Oxaphosphetane("CC[C@@H]1[C@@H](C2=CC=C3C(=C2)N=C4C=CC=CC4=N3)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # SUCCESS
        # oxaphos = Oxaphosphetane("C[C@@H]1OP2(c3ccccc3)(c3ccccc3-c3ccccc32)[C@H]1C(=O)c1ccccc1")  # FAILED
        # oxaphos = Oxaphosphetane("C=CCCCCCCCC[C@]1(C(=O)OC)[C@@H](C(C)c2ccccc2)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # FAILED
        oxaphos = Oxaphosphetane("CCOC(=O)[C@]1(C)[C@@H](CCl)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # FAILED
        # oxaphos = Oxaphosphetane("COC(=O)[C@@H]1[C@H](C2=C[C@H](O)[C@H]3OC(C)(C)O[C@H]3O2)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # SUCCESS
        # oxaphos = Oxaphosphetane("CCOC(=O)[C@@H]1[C@@H]([C@@H]2OC(C)(C)O[C@H]2COCc2ccccc2)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # SUCCESS
        # oxaphos = Oxaphosphetane("CCOC(=O)[C@@H]1[C@@H]([C@@H]2OC(C)(C)O[C@H]2CO[Si](C)(C)C(C)(C)C)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # SUCCESS
        # oxaphos = Oxaphosphetane("CCOC(=O)[C@@H]1[C@H]([C@H]2O[C@@H]3OC(C)(C)O[C@@H]3[C@H]2OCc2ccccc2)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # SUCCESS
        # oxaphos = Oxaphosphetane("CCOC(=O)[C@]1(C)[C@H](CS)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # SUCCESS
        # oxaphos = Oxaphosphetane("CCOC(=O)[C@]1(C)[C@H]([C@@H]2O[C@@H]2[C@H]2O[C@@H](c3ccccc3)OC[C@@H]2O)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # SUCCESS
        # oxaphos = Oxaphosphetane("CCC[C@@H]1[C@@]2(CCC3C4CCc5cc(OC)ccc5C4CC[C@@]32C)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")  # FAILED
        # oxaphos = Oxaphosphetane("CCCCC[C@H]1OP(c2ccccc2)(c2ccccc2)(c2ccccc2)[C@@H]1/C=C/CO")  # SUCCESS
        # oxaphos = Oxaphosphetane("C[Si](C)(C)C#C[C@@H]1[C@@H](C2CCCCO2)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")
        print("Molecular Formula:", oxaphos.get_formula())
        print("Number of Atoms:", oxaphos.num_atoms())
        print("Canonical SMILES:", oxaphos.get_canonical_smiles())
        print("Constraint:", Chem.MolToSmiles(Chem.RemoveAllHs(oxaphos.constraint_core_mol)))
        print()
        print(oxaphos.generate_3d_coordinates(optimize=True, constrain_opt=False))
        oxaphos.visualize_3d(label='ALPHATEST')
    except ValueError as e:
        print(e)
