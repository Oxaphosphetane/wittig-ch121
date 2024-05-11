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

    def embed_3d(self, max_attempts=10):
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
        if self.embed_3d():
            if optimize:
                self.optimize_3d(force_field)
        else:
            raise Exception("Failed to embed molecule, cannot proceed with optimization.")

    def visualize_3d(self, label=''):
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
    core_ring_smiles = 'C1COP1'
    path_to_templates = os.path.join(nav.find_root(), 'saved_files')

    def __init__(self, r1='C', r2='C'):
        self.sdf_reader = Chem.SDMolSupplier(os.path.join(OxaphosEmbedParams.path_to_templates, 'OP_templates.sdf'), removeHs=False)
        self.cis_template_mols = (self.sdf_reader[0], self.sdf_reader[1])
        self.trans_template_mols = (self.sdf_reader[2], self.sdf_reader[3])


class Oxaphosphetane(Molecule):
    def __init__(self, smiles: str):
        super().__init__(smiles)
        # Initialize any Oxaphosphetane-specific properties if needed
        self.ring_indices = self.get_ring_indices()
        self.cis_templates = self.make_cis_templates()

    def get_ring_indices(self):
        """Return ring indices in format (c1_idx, c2_idx, o_idx, p_idx)."""
        ring_template = Chem.MolFromSmiles(OxaphosEmbedParams.core_ring_smiles)
        matches = self.molecule_with_hydrogens.GetSubstructMatches(ring_template)

        try:
            return matches[0]
        except IndexError:
            raise Exception("Molecule is not an oxaphosphetane.")

    def find_chain_leads(self):
        c1_idx, c2_idx = self.ring_indices[0], self.ring_indices[1]

        c1_atom = self.molecule_with_hydrogens.GetAtomWithIdx(c1_idx)
        c2_atom = self.molecule_with_hydrogens.GetAtomWithIdx(c2_idx)

        def find_chain(ring_atom):
            neighbors = ring_atom.GetNeighbors()
            for neighbor in neighbors:
                if neighbor.GetIdx() not in self.ring_indices and neighbor.GetSymbol() != 'H':
                    return neighbor

        return tuple(map(find_chain, (c1_atom, c2_atom)))

    def make_cis_templates(self):
        nb1, nb2 = self.find_chain_leads()
        R1, R2 = nb1.GetSymbol(), nb2.GetSymbol()

        return f"{R1}[C@H]1[C@@H]({R2})OP1", f"{R1}[C@@H]1[C@H]({R2})OP1"

    def make_trans_templates(self):
        R1, R2 = self.find_chain_leads()

        return f"{R1}[C@H]1[C@H]({R2})OP1", f"{R1}[C@@H]1[C@@H]({R2})OP1"

    def is_cis(self):
        """Checks if a molecule is cis-disubstituted."""
        # Perform the substructure search with stereochemistry consideration
        for template in self.make_cis_templates():
            if self.molecule_with_hydrogens.HasSubstructMatch(Chem.MolFromSmiles(template), useChirality=True):
                return True

        return False

    def is_trans(self):
        """Checks if a molecule is trans-disubstituted."""
        for template in self.make_trans_templates():
            if self.molecule_with_hydrogens.HasSubstructMatch(Chem.MolFromSmiles(template), useChirality=True):
                return True

        return False

    def embed_3d(self, max_attempts=10):
        params = OxaphosEmbedParams()

        if self.is_cis():
            template_molecule = params.cis_template_mols
        elif self.is_trans():
            template_molecule = params.trans_template_mols
        else:
            raise ValueError("Molecule is not cis or trans-disubstituted.")

        # Perform the constrained embedding
        try:
            # Attempt to match the core structure and constrain the embedding
            cid = AllChem.ConstrainedEmbed(self.molecule_with_hydrogens, template_molecule)
            print("Constrained embedding successful, conformation ID:", cid)
            return True
        except ValueError as e:
            print("Constrained embedding failed:", e)
            return False

    def optimize_3d(self, force_field=ForceFieldMethod.UFF):
        # Assume that the molecule_with_hydrogens has a valid 3D conformation at this point
        if force_field == ForceFieldMethod.UFF:
            ff = AllChem.UFFGetMoleculeForceField(self.molecule_with_hydrogens)
        elif force_field == ForceFieldMethod.MMFF:
            props = AllChem.MMFFGetMoleculeProperties(self.molecule_with_hydrogens)
            ff = AllChem.MMFFGetMoleculeForceField(self.molecule_with_hydrogens, props)
        else:
            raise ValueError("Unsupported force field. Choose 'uff' or 'mmff'.")

        # Apply constraints to the core atoms
        ring_indices = self.get_ring_indices()  # Assuming this method returns indices of the core atoms
        for idx in ring_indices:
            ff.AddFixedPoint(idx)

        if ff is not None:
            ff.Minimize(500)  # Perform the optimization
            print("Optimization successful")
        else:
            raise Exception("Failed to create force field for optimization.")

    def visualize_with_template(self):
        pass


# Example usage:
try:
    oxaphos = Oxaphosphetane("CC[C@H]1[C@H](CC)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")
    print("Molecular Formula:", oxaphos.get_formula())
    print("Number of Atoms:", oxaphos.num_atoms())
    print("Canonical SMILES:", oxaphos.get_canonical_smiles())
    params = OxaphosEmbedParams()

    print('cis matches')
    for i, temp_mol in enumerate(params.cis_template_mols):
        match = oxaphos.molecule_with_hydrogens.HasSubstructMatch(Chem.RemoveAllHs(temp_mol), useChirality=True)
        print(match)
        if match:
            OP = Oxaphosphetane.from_rdkit_mol(temp_mol)
            OP.visualize_3d(label='CISMATCH')

    print('trans matches')
    for temp_mol in params.trans_template_mols:
        match = oxaphos.molecule_with_hydrogens.HasSubstructMatch(Chem.RemoveAllHs(temp_mol), useChirality=True)
        print(match)
        if match:
            OP = Oxaphosphetane.from_rdkit_mol(temp_mol)
            OP.visualize_3d(label='TRANSMATCH')
    # oxaphos.embed_3d()
    # oxaphos.visualize_3d()
    # oxaphos.generate_3d_coordinates(optimize=True)
    # OP = Oxaphosphetane.from_rdkit_mol(OxaphosEmbedParams.template_molecule)
    # OP.visualize_3d()
except ValueError as e:
    print(e)


# oxaphos = Oxaphosphetane("CC[C@H]1[C@H](CC)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")
# print("Molecular Formula:", oxaphos.get_formula())
# print("Number of Atoms:", oxaphos.num_atoms())
# print("Canonical SMILES:", oxaphos.get_canonical_smiles())
# print(oxaphos.make_cis_templates())
# print(oxaphos.is_cis())
# print(oxaphos.is_trans())
# print(Chem.MolToMolBlock(oxaphos.molecule_with_hydrogens))


