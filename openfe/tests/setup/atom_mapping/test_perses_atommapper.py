# This code is part of OpenFE and is licensed under the MIT license.
# For details, see https://github.com/OpenFreeEnergy/openfe
import pytest
from rdkit import Chem


import openfe
from openfe.setup import SmallMoleculeComponent
from openfe.setup.atom_mapping import PersesAtomMapper

def test_simple(lomap_basic_test_files):
    # basic sanity check on the LigandAtomMapper
    mol1 = lomap_basic_test_files['methylcyclohexane']
    mol2 = lomap_basic_test_files['toluene']

    mapper = PersesAtomMapper()

    mapping_gen = mapper.suggest_mappings(mol1, mol2)

    mapping = next(mapping_gen)
    assert isinstance(mapping, openfe.setup.atom_mapping.LigandAtomMapping)
    # maps (CH3) off methyl and (6C + 5H) on ring
    assert len(mapping.molA_to_molB) == 4


def test_generator_length(lomap_basic_test_files):
    # check that we get one mapping back from Lomap LigandAtomMapper then the
    # generator stops correctly
    mol1 = lomap_basic_test_files['methylcyclohexane']
    mol2 = lomap_basic_test_files['toluene']

    mapper = PersesAtomMapper()

    mapping_gen = mapper.suggest_mappings(mol1, mol2)

    _ = next(mapping_gen)
    with pytest.raises(StopIteration):
        next(mapping_gen)


def test_bad_mapping(lomap_basic_test_files):
    toluene = lomap_basic_test_files['toluene']
    NigelTheNitrogen = SmallMoleculeComponent(Chem.MolFromSmiles('N'), name='Nigel')

    mapper = PersesAtomMapper()

    mapping_gen = mapper.suggest_mappings(toluene, NigelTheNitrogen)
    with pytest.raises(StopIteration):
        i=0
        while True:
            next(mapping_gen)
            if(i>1000):
                raise Exception("this is an inf loop... but should not be!")
            else:
                i+=1

