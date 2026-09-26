"""M5Stack's official STL (m5stack/M5_Hardware, MIT, pinned commit) for the 3D previews of the station scripts.
Downloaded once into station/cad/ (git-ignored); the preview pages show the meshes, nothing is written back."""
import os, urllib.request
import numpy as np

M5HW = 'https://raw.githubusercontent.com/m5stack/M5_Hardware/a240115c94b19ecf647f229c47fa9a8ce46ccdc4/Products/'
# file, and which triangles are the assembled copy (each file also holds an exploded copy), by their centres
CAD = {'core': ('K128-SE_CoreS3-SE/Structures/CoreS3-SE.stl', lambda c: c[:, 2] > -30),
       'nfc': ('U216_Unit_NFC/Structures/Unit_NFC.stl', lambda c: c[:, 0] < 15),
       'voice': ('C126-ECHO_Atom_VoiceS3R/Structures/Atom_VoiceS3R.stl', lambda c: c[:, 0] < 15)}
CAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cad')


def stl_tris(key):
    """Triangles (n, 3, 3) of the assembled copy in an official M5Stack STL (binary), in the STL's own coordinates."""
    rel, keep = CAD[key]
    path = os.path.join(CAD_DIR, os.path.basename(rel))
    if not os.path.exists(path):
        os.makedirs(CAD_DIR, exist_ok=True)
        urllib.request.urlretrieve(M5HW + rel, path)
    raw = open(path, 'rb').read()
    n = int(np.frombuffer(raw, '<u4', 1, 80)[0])
    rec = np.frombuffer(raw, np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), n, 84)
    t = rec['v']
    return t[keep(t.mean(axis=1))]
