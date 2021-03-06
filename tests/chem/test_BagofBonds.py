import pytest
import numpy as np

from chemml.chem import BagofBonds
from chemml.chem import Molecule
from chemml.chem import XYZ

@pytest.fixture()
def mols():
    # Oxygen, Hydrogen, Hydrogen
    num = np.array([8, 1, 1])
    num = num.reshape((3, 1))
    sym = np.array(['O', 'H', 'H'])
    sym = sym.reshape((3, 1))
    c = np.array([[1.464, 0.707, 1.056], [0.878, 1.218, 0.498], [2.319, 1.126, 0.952]])
    xyz = XYZ(c,num,sym)
    m = Molecule('O', 'smiles')
    # forcefully overwrite xyz
    m._xyz = xyz
    return m

def test_h2o(mols):
    bob = BagofBonds(const=1.0)
    h2o = bob.represent(mols)

    assert h2o.shape == (1, 6)
    a = np.array([[0.66066557, 0.5, 0.5, 8.3593106, 8.35237809, 73.51669472]])
    assert a[0][0] == pytest.approx( h2o.values[0][0])
    assert a[0][1] == pytest.approx(h2o.values[0][1])
    assert a[0][-1] == pytest.approx(h2o.values[0][-1])



