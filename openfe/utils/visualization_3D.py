import py3Dmol
import numpy as np
from typing import Tuple


from rdkit import Chem
from rdkit.Geometry.rdGeometry import Point3D
from matplotlib import pyplot as plt
from matplotlib.colors import rgb2hex

from gufe.mapping import AtomMapping

 
def draw_mapping_on_3Dstructure(
    edge: AtomMapping,
    spheres: bool = True,
    show_atomIDs: bool = False,
    style: str = "stick",
    shift: Tuple[float, float, float] = (10, 0, 0),
) -> py3Dmol.view:

    """
    Render relative transformation edge in 3D using py3Dmol.

    By default matching atoms will be annotated using colored spheres.

    Parameters
    ----------
    edge : LigandAtomMapping
        The ligand transformation edge to visualize.
    spheres : bool
        Whether or not to show matching atoms as spheres.
    style : str
        Style in which to represent the molecules in py3Dmol.
    shift : Tuple of floats
        Amount to shift molB by in order to visualise the two ligands.
        By default molB is shifted by 10 A in the z direction.

    Returns
    -------
    view : py3Dmol.view
        View of the system containing both molecules in the edge.
    """
    shift = np.array(shift)

    def translate(mol, shift):
        conf = mol.GetConformer()
        for i, atom in enumerate(mol.GetAtoms()):
            x, y, z = conf.GetAtomPosition(i)
            point = Point3D(x + shift[0], y + shift[1], z + shift[2])
            conf.SetAtomPosition(i, point)
        return mol

    def add_spheres(view, mol1, mol2, mapping):
        # Get colourmap of size mapping
        cmap = plt.cm.get_cmap("hsv", len(mapping))
        for i, pair in enumerate(mapping.items()):
            p1 = mol1.GetConformer().GetAtomPosition(pair[0])
            p2 = mol2.GetConformer().GetAtomPosition(pair[1])
            color = rgb2hex(cmap(i))
            view.addSphere(
                {
                    "center": {"x": p1.x, "y": p1.y, "z": p1.z},
                    "radius": 0.6,
                    "color": color,
                    "alpha": 0.8,
                }
            )
            view.addSphere(
                {
                    "center": {"x": p2.x, "y": p2.y, "z": p2.z},
                    "radius": 0.6,
                    "color": color,
                    "alpha": 0.8,
                }
            )

    molA = edge.componentA.to_rdkit()
    molB = edge.componentB.to_rdkit()

    mblock1 = Chem.MolToMolBlock(translate(molA, -1 * shift))
    mblock2 = Chem.MolToMolBlock(translate(molB, shift))

    view = py3Dmol.view(width=600, height=600)
    view.addModel(mblock1, "molA")
    view.addModel(mblock2, "molB")

    if spheres:
        add_spheres(view, molA, molB, edge.componentA_to_componentB)

    if show_atomIDs:
        view.addPropertyLabels(
            "index",
            {"not": {"resn": ["molA_overlay", "molA_overlay"]}},
            {
                "fontColor": "black",
                "font": "sans-serif",
                "fontSize": "10",
                "showBackground": "false",
                "alignment": "center",
            },
        )

    # middle fig
    overlay_mblock1 = Chem.MolToMolBlock(translate(molA, 1 * shift))
    overlay_mblock2 = Chem.MolToMolBlock(translate(molB, -1 * shift))

    view.addModel(overlay_mblock1, "molA_overlay")
    view.addModel(overlay_mblock2, "molB_overlay")

    view.setStyle({style: {}})

    view.zoomTo()
    return view
