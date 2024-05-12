from typing import Tuple, Any

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Draw, AllChem, rdFMCS
import os
import os_navigation as nav


class ForceFieldMethod:
    UFF = 'uff'
    MMFF = 'mmff'


class Molecule:
    def __init__(self, smiles: str):
        self.molecule = Chem.MolFromSmiles(smiles)
        if self.molecule is None:
            raise ValueError("Invalid SMILES string provided")
        self.molecule_with_hydrogens = Chem.AddHs(self.molecule)
        self.canonical_smiles = Chem.MolToSmiles(self.molecule, isomericSmiles=True)

    @classmethod
    def from_rdkit_mol(cls, mol):
        smi = Chem.MolToSmiles(mol, isomericSmiles=True)
        m = cls(smi)
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

    def embed_3d(self, max_attempts=5) -> bool:
        params = AllChem.ETKDGv3()
        params.numThreads = 0
        for attempt in range(max_attempts):
            params.randomSeed = 42 + attempt
            status = AllChem.EmbedMolecule(self.molecule_with_hydrogens, params)
            if status == 0:
                return True
        return False

    def optimize_3d(self, force_field=ForceFieldMethod.UFF):
        if force_field == ForceFieldMethod.UFF:
            ff = AllChem.UFFGetMoleculeForceField(self.molecule_with_hydrogens)
        elif force_field == ForceFieldMethod.MMFF:
            ff = AllChem.MMFFGetMoleculeForceField(self.molecule_with_hydrogens, AllChem.MMFFGetMoleculeProperties(self.molecule_with_hydrogens))
        else:
            raise ValueError("Unsupported force field. Choose 'uff' or 'mmff'.")

        if ff is not None:
            ff.Minimize(500)
        else:
            raise Exception("Failed to create force field for optimization.")

    def generate_3d_coordinates(self, optimize=True, force_field=ForceFieldMethod.UFF):
        if self.embed_3d():  # modifies Molecule in place and returns bool True if success
            if optimize:
                self.optimize_3d(force_field)
        else:
            raise Exception("Failed to embed molecule, cannot proceed with optimization.")

    def visualize_3d(self, label='') -> str:
        mb = Chem.MolToMolBlock(self.molecule_with_hydrogens)
        mb_escaped = mb.replace('\n', '\\n').replace('\'', '\\\'').replace('\"', '\\"')
        html = """
        <html>
        <head>
            <title>Molecule Visualization</title>
            <script src="https://3Dmol.csb.pitt.edu/build/3Dmol-min.js"></script>
        </head>
        <body>
            <div id="molDiv" style="height: 400px; width: 800px; position: relative;"></div>
            <script>
                var config = {{ backgroundColor: 'white' }};
                var viewer = $3Dmol.createViewer(document.getElementById('molDiv'), config);
                var molData = `{0}`;
                viewer.addModel(molData, 'sdf');
                viewer.setStyle({{}}, {{stick: {{radius: 0.15}}, sphere: {{radius: 0.3}}}});
                viewer.zoomTo();
                viewer.render();
            </script>
        </body>
        </html>
        """.format(mb_escaped)
        with open(f'molecule_visualization_test_{label}.html', 'w') as f:
            f.write(html)
        print("3D visualization written to 'molecule_visualization_test.html'. Open this file in a web browser to view the molecule.")
        return html

    def get_canonical_smiles(self):
        return self.canonical_smiles


class OxaphosEmbedParams:
    """Create 3D embedding parameters for an Oxaphosphetane."""
    cis_pph3_sdf_idxs = [0, 1]
    trans_pph3_sdf_idxs = [2, 3]
    cis_chop_sdf_idxs = [4, 5]
    trans_chop_sdf_idxs = [6, 7]

    path_to_templates = os.path.join(nav.find_root(), 'saved_files')

    core_ring_smiles = 'C1COP1'
    core_ring_pph3_smiles = 'C1COP1(c1ccccc1)(c1ccccc1)c1ccccc1'

    def __init__(
        self,
        oxaphos_mol: Chem.Mol,
        is_triphenyl=True,
        is_cis=True,
        ligand_atoms: tuple = None,
        chain_atoms: tuple = None,
    ):
        self.sdf_reader = Chem.SDMolSupplier(os.path.join(OxaphosEmbedParams.path_to_templates, 'OP_templates.sdf'), removeHs=False)
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
        rw_mol = Chem.RWMol(mol)   # Create an editable molecule from the original molecule
        rw_mol.ReplaceAtom(atom_index, Chem.Atom(new_atomic_num))  # Replace the specified atom with a new atom of the specified type
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
    def __init__(self, smiles: str):
        super().__init__(smiles)
        # Initialize any Oxaphosphetane-specific properties if needed
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

        if self.molecule_with_hydrogens.HasSubstructMatch(triphenyl_ring_template):
            return True

        return False

    def embed_3d(self, max_attempts=10) -> bool:
        # Perform the constrained embedding
        try:
            # Attempt to match the core structure and constrain the embedding
            cid = AllChem.ConstrainedEmbed(self.molecule_with_hydrogens, Chem.RemoveAllHs(self.constraint_core_mol))
            print("Constrained embedding successful, conformation ID:", cid)
            return True
        except ValueError as e:
            print("Constrained embedding failed:", e)
            return False

    def optimize_3d(self, force_field=ForceFieldMethod.UFF):
        # First, find the matching substructure to apply constraints
        match = self.molecule_with_hydrogens.GetSubstructMatch(Chem.RemoveAllHs(self.constraint_core_mol))
        if not match:
            raise Exception("Core structure not found in the molecule.")

        # Set up the force field
        if force_field == ForceFieldMethod.UFF:
            ff = AllChem.UFFGetMoleculeForceField(self.molecule_with_hydrogens)
        elif force_field == ForceFieldMethod.MMFF:
            ff = AllChem.MMFFGetMoleculeForceField(self.molecule_with_hydrogens,
                                                   AllChem.MMFFGetMoleculeProperties(self.molecule_with_hydrogens))
        else:
            raise ValueError("Unsupported force field. Choose 'uff' or 'mmff'.")

        if ff is None:
            raise Exception("Failed to create force field for optimization.")

        # Apply constraints to the matched core atoms
        for idx in match:
            ff.AddFixedPoint(idx)

        # Perform the optimization
        ff.Minimize(500)
        print("Optimization with constrained core successful.")


# Example usage:
try:
    oxaphos = Oxaphosphetane("CC[C@H]1[C@H](CC)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")
    print("Molecular Formula:", oxaphos.get_formula())
    print("Number of Atoms:", oxaphos.num_atoms())
    print("Canonical SMILES:", oxaphos.get_canonical_smiles())
    print("Constraint:", Chem.MolToSmiles(Chem.RemoveAllHs(oxaphos.constraint_core_mol)))
    oxaphos.generate_3d_coordinates(optimize=True)
    oxaphos.visualize_3d(label='ALPHATEST')
except ValueError as e:
    print(e)