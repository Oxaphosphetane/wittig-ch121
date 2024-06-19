## Things to work on

- Sn doesn't work with `6-31G**` basis set
- pass in `Enum` instead of `Enum.value` for method and basis
- fix the `[O]` product entries in `all_dfs.json`
- bug in rdkit sdf reader `[P@TB]` nonsense

- implement `molecule.Molecule.infer_bonds_from_coordinates()` <- last resort/overkill!

- entry 98 in all_dfs.json has
  `[H]C([C@H](OC(C1=CC=CC=C1)=O)[C@@H]([C@@](COC(C2=CC=CC=C2)=O)(OC(C3=CC=CC=C3)=O)[H])OC(C4=CC=CC=C4)=O)=O`,
  which is not equal to canonical smiles, used as testing (mol_id = 701)

- change runtime estimator to simple monomial x^p with p \in [2,3]

- generate wittig_molecules_expanded.csv library with different *phosphines*.

