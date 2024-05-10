from rdkit import Chem
from rdkit.Chem import rdMolDescriptors, Draw, AllChem


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

    def visualize_3d(self):
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
        with open('molecule_visualization.html', 'w') as f:
            f.write(html)
        print("3D visualization written to 'molecule_visualization.html'. Open this file in a web browser to view the molecule.")
        return html

    def get_canonical_smiles(self):
        return self.canonical_smiles


class Oxaphosphetane(Molecule):
    BASE_RING_TEMPLATE = Chem.MolFromSmiles('C1C')
    def __init__(self, smiles: str):
        super().__init__(smiles)
        # Initialize any Oxaphosphetane-specific properties if needed
        self.template = None  # This could be a template molecule or coordinates
        self.cis_templates = (
            Chem.MolFromSmiles("[C@H]1[C@@H]([!#1])OP(*)(*)(*)1", sanitize=True),
            Chem.MolFromSmiles()# the enantiotopic cis template is: *[C@@H]1[C@H](*)OP1

    def is_cis(self):
        # Perform the substructure search with stereochemistry consideration
        match = self.molecule_with_hydrogens.HasSubstructMatch(self.cis_template, useChirality=True)
        return match

    def apply_template(self):
        # Apply a structural template to the molecule before embedding
        # Placeholder: Implement template application logic here
        print("Template application logic goes here.")

    def specialized_optimization(self):
        # Overriding the general optimization to include template-based constraints
        self.apply_template()
        super().generate_3d_coordinates(optimize=True)
        # Additional Oxaphosphetane-specific optimization steps can go here

    def visualize_with_template(self):
        # Optional: Special method to visualize with template highlighted
        print("Visualization with template highlighted goes here.")

# Example usage:
try:
    oxaphos = Molecule("CC[C@H]1[C@H](CC)OP1(c1ccccc1)(c1ccccc1)c1ccccc1")
    print("Molecular Formula:", oxaphos.get_formula())
    print("Number of Atoms:", oxaphos.num_atoms())
    print("Canonical SMILES:", oxaphos.get_canonical_smiles())
    oxaphos.generate_3d_coordinates(optimize=True)
    oxaphos.visualize_3d()
except ValueError as e:
    print(e)