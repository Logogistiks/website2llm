#!/.venv/Scripts/python.exe

import llm
import json
import configparser
import sqlite_utils

def getcfg(filename: str="config.cfg") -> dict:
    cfgparser = configparser.RawConfigParser()
    cfgparser.read(filename)
    return dict(cfgparser.items("default"))

def interact(userprompt: str, conv: llm.Conversation, verbose: bool=False) -> str:
    db = sqlite_utils.Database("embeddings.db")
    collection = llm.Collection("default", db)
    if verbose: print("Comparing Embedding Vectors...")
    similar = [entry.id for entry in collection.similar(userprompt, number=3)]
    if verbose: print("Loading needed Data from file...")
    with open("data.json", "r") as f:
        data = json.load(f)
    entrycontent = [entry["content"] for entry in data if str(entry["id"]) in similar]
    info = ("#"*10).join(entrycontent)
    prompt = "Dies ist die Frage des Users:\n" + userprompt + "\nBitte beantworte diese Frage mithilfe folgender Daten:\n" + info
    if verbose: print("Generating Response...")
    return conv.prompt(prompt).text()

if __name__ == "__main__":
    config = getcfg()
    model = llm.get_model(config["answermodel"])
    conversation = model.conversation()
    while True:
        userinput = input(">>> ")
        response = interact(userinput, conversation)
        print(response)