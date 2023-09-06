import llm
import json
import configparser
import sqlite_utils

def getcfg(filename: str="config.cfg") -> dict:
    cfgparser = configparser.RawConfigParser()
    cfgparser.read(filename)
    return dict(cfgparser.items("default"))

def interact(userprompt: str, handler: llm.Model|llm.models.Conversation=None, verbose: bool=False) -> str:
    """Return an Answer to given prompt when supplied with a model or a conversation"""
    if not isinstance(handler, llm.Model) and not isinstance(handler, llm.models.Conversation):
        return "Error: Neither Model or Conversation Provided"
    db = sqlite_utils.Database("embeddings.db")
    collection = llm.Collection("default", db)
    if verbose: print("Comparing Embedding Vectors...")
    similar = [entry.id for entry in collection.similar(userprompt, number=3)]
    if verbose: print("Loading needed Data from file...")
    with open("data.json", "r") as f:
        data = json.load(f)
    entrycontent = [entry["content"] for entry in data if str(entry["id"]) in similar]
    info = ("#"*10).join(entrycontent)
    prompt = "Dies ist die Frage des Users:\n" + userprompt + "\nBitte beantworte diese Frage und richte dich dabei an den User. Bitte gib nur die Antwort zurück. Nutze dazu bitte folgende Daten:\n" + info
    if verbose: print("Generating Response...")
    return handler.prompt(prompt).text()

if __name__ == "__main__":
    config = getcfg()
    model = llm.get_model(config["answermodel"])
    conversation = model.conversation()
    while True:
        userinput = input(">>> ")
        response = interact(userinput, conversation)
        print(response)