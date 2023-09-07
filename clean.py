import os # preinstalled

for file in ["data.json", "embeddings.db", ".venv", "config.cfg"]:
    os.remove(file)