import os, pathlib
_FOLDER =  pathlib.Path(__file__).parent / 'mocked_json'

# Load all mocked json from mocked_json folder
for f in os.listdir(_FOLDER):
    if f.endswith('.json'):
        globals()[f.upper().replace('.','_')] = pathlib.Path(_FOLDER / f).read_text()
