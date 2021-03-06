import pytest
import numpy as np

from chemml.chem import CoulombMatrix
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

def test_exception(mols):
    # Value error: molecule object
    cm = CoulombMatrix('UM')
    with pytest.raises(ValueError):
        cm.represent('fake')
    with pytest.raises(ValueError):
        cm.represent(['fake'])
    # Value error ndim>1
    with pytest.raises(ValueError):
        cm.represent(np.array([[mols],[mols]]))

def test_UM(mols):
    cm = CoulombMatrix('UM')
    h2o = cm.represent(mols)
    assert h2o.shape == (1, cm.max_n_atoms**2)
    a = np.array([[
        73.51669472, 8.3593106, 8.35237809, 8.3593106, 0.5, 0.66066557, 8.35237809, 0.66066557, 0.5
    ]])
    assert a[0][0] == pytest.approx(h2o.values[0][0], 0.001)
    assert a[0][1] == pytest.approx(h2o.values[0][1], 0.001)
    assert a[0][-1] == pytest.approx(h2o.values[0][-1], 0.001)

def test_UT(mols):
    cm = CoulombMatrix('UT')
    h2o = cm.represent(mols )

    assert h2o.shape == (1, cm.max_n_atoms * (cm.max_n_atoms + 1) / 2)
    a = np.array([[73.51669472, 8.3593106, 0.5, 8.35237809, 0.66066557, 0.5]])
    assert a[0][0] == pytest.approx(h2o.values[0][0])
    assert a[0][1] == pytest.approx(h2o.values[0][1])
    assert a[0][-1] == pytest.approx(h2o.values[0][-1])

def test_E(mols):
    cm = CoulombMatrix('E')
    h2o = cm.represent(mols )

    assert h2o.shape == (1, cm.max_n_atoms)
    a = np.array([[75.39770052, -0.16066482, -0.72034098]])
    assert a[0][0] == pytest.approx( h2o.values[0][0])
    assert a[0][1] == pytest.approx( h2o.values[0][1])
    assert a[0][-1] == pytest.approx( h2o.values[0][-1])

def test_SC(mols):
    cm = CoulombMatrix('SC')
    h2o = cm.represent(mols )

    assert h2o.shape == (1, cm.max_n_atoms * (cm.max_n_atoms + 1) / 2)
    a = np.array([[73.51669472, 8.3593106, 0.5, 8.35237809, 0.66066557, 0.5]])
    assert a[0][0] == pytest.approx( h2o.values[0][0])
    assert a[0][1] == pytest.approx( h2o.values[0][1])
    assert a[0][-1] == pytest.approx( h2o.values[0][-1])

def test_RC(mols):
    cm = CoulombMatrix('RC')
    h2o = cm.represent(mols )

    assert h2o.shape == (1, cm.nPerm * cm.max_n_atoms * (cm.max_n_atoms + 1) / 2)
    a = np.array([[
        0.5, 8.35237809, 73.51669472, 0.66066557, 8.3593106, 0.5, 73.51669472, 8.35237809, 0.5,
        8.3593106, 0.66066557, 0.5, 0.5, 8.3593106, 73.51669472, 0.66066557, 8.35237809, 0.5
    ]])
