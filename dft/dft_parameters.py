import enum
import molecule as mol
from rdkit import Chem
import numpy as np
from abc import ABC, abstractmethod


class JaguarInputParams:
    HEADER = '&gen'
    ENTRY_NAME = 'entry_name'
    BASIS = 'basis'
    DFT_NAME = 'dftname'
    Z_MAT = '&zmat'
    IGEOPT = 'igeopt'
    IFREQ = 'ifreq'
    COORD = '&coord'
    ZVAR = '&zvar'


class _DFTParam:
    def __init__(self, code: int, name: str, jaguar_name: str):
        self.code = code
        self.name = name
        self.jaguar_name = jaguar_name



"""
dft methods
"""


class _DFTMethod(_DFTParam):
    def __init__(self, code: int, name: str, jaguar_name: str, runtime_estimator: list[float] = None):
        super().__init__(code, name, jaguar_name)
        self.runtime_estimator = np.poly1d(runtime_estimator)

    def __repr__(self):
        return f"_DFTMethod(code={self.code}, jaguar_name='{self.jaguar_name}')"


class DFTMethods(enum.Enum):
    PBE = _DFTMethod(0, 'pbe', 'PBE')
    B3LYP = _DFTMethod(1, 'b3lyp', 'B3LYP')
    PBE_D3 = _DFTMethod(2, 'pbe-d3', 'PBE-D3',
                        [1.06482738e-08, -4.61542348e-06, 7.92766672e-04, -6.89593731e-02,
                         3.23848009e+00, -7.96960678e+01, 9.67486090e+02, -4.24036733e+03])
    B3LYP_D3 = _DFTMethod(3, 'b3lyp-d3', 'B3LYP-D3')

    @classmethod
    def from_code(cls, code: int):
        for method in cls:
            if method.value.code == code:
                return method
        return None

    @classmethod
    def from_name(cls, name: str):
        for method in cls:
            if method.value.name.lower() == name.lower():
                return method
        return None


"""
dft bases
"""


class _DFTBasis(_DFTParam):
    def __init__(self, code: int, name: str, jaguar_name: str):
        super().__init__(code, name, jaguar_name)

    def __repr__(self):
        return f"_DFTBasis(code={self.code}, jaguar_name='{self.jaguar_name}')"


class DFTBases(enum.Enum):
    GAUSS_6_31 = _DFTBasis(0, '6-31g', '6-31G')
    GAUSS_6_31_SS = _DFTBasis(1, '6-31g**', '6-31G**')
    DEF2_TZVP = _DFTBasis(2, 'def2-tzvp', 'DEF2-TZVP')
    DEF2_TZVP_F = _DFTBasis(3, 'def2-tzvp(-f)', 'DEF2-TZVP(-F)')

    @classmethod
    def from_code(cls, code: int):
        for basis in cls:
            if basis.value.code == code:
                return basis
        return None

    @classmethod
    def from_name(cls, name: str):
        for basis in cls:
            if basis.value.name.lower() == name.lower():
                return basis
        return None


"""
scans
"""


class _RCScanType:
    def __init__(self, code: int, scan_type: str, jaguar_var_name: str, n_atoms: int):
        self.code = code
        self.scan_type = scan_type,
        self.jaguar_scan_type_name = jaguar_var_name
        self.n_atoms = n_atoms


class RCScanTypes(enum.Enum):
    DISTANCE = _RCScanType(0, 'DISTANCE', 'r', n_atoms=2)
    ANGLE = _RCScanType(1, 'ANGLE', 'a', n_atoms=3)
    DIHEDRAL = _RCScanType(2, 'DIHEDRAL', 'd', n_atoms=4)
    X_CARTESIAN = _RCScanType(3, 'CARTESIAN-X', 'x', n_atoms=1)
    Y_CARTESIAN = _RCScanType(4, 'CARTESIAN-Y', 'y', n_atoms=1)
    Z_CARTESIAN = _RCScanType(5, 'CARTESIAN-Z', 'z', n_atoms=1)

    @classmethod
    def from_code(cls, code: int):
        for method in cls:
            if method.value.code == code:
                return method
        return None


class RCScan:
    def __init__(
            self,
            molecule: mol.Molecule,
            atoms: tuple[Chem.Atom],
            scan_start: int or float,
            scan_end: int or float,
            n_steps: int,
            scan_type: RCScanTypes
    ):
        assert len(atoms) == scan_type.value.n_atoms
        assert scan_start < scan_end

        self.molecule = molecule
        self.atoms = atoms
        self.RCScanType = scan_type
        self.start = scan_start
        self.end = scan_end
        self.n_steps = n_steps
        self.step_size = self.get_step_size()

    def get_step_size(self) -> float:
        return (self.end - self.start) / (self.n_steps - 1)
