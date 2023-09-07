import os # preinstalled

for file in ["data.json", "embeddings.db", "config.cfg"]:
    if os.path.exists(file):
        os.remove(file)