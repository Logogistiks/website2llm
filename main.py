import llm
import configparser
import sqlite_utils
import time

def getcfg(filename: str="config.cfg", section: str="default") -> dict:
    """Load config properties from config file"""
    cfgparser = configparser.RawConfigParser()
    cfgparser.read(filename)
    return dict(cfgparser.items(section))

def interact(userprompt: str, handler: llm.Model|llm.models.Conversation=None, verbose: bool=False) -> str:
    """Return an Answer to given prompt when supplied with a model or a conversation"""
    cfg = getcfg()
    if not isinstance(handler, llm.Model) and not isinstance(handler, llm.models.Conversation):
        return "Error: Neither Model or Conversation Provided"
    db = sqlite_utils.Database("embeddings.db")
    collection = llm.Collection("default", db)
    if verbose: print("Comparing Embedding Vectors...")
    similar = [entry.content for entry in collection.similar(userprompt, number=cfg["similarnum"])]
    info = ("#"*10).join(similar)
    if verbose: print(info)
    prompt = "Frage:\n" + userprompt + "\nBitte beantworte diese Frage. Bitte gib nur die Antwort zurück. Wenn die Antwort aus den folgenden Daten nicht ersichtlich ist, ein Name beispielsweise nicht vorkommt, gib bitte zurück, dass du die Antwort nicht weißt. Nutze dazu bitte folgende Daten:\n" + info
    if verbose: print("Generating Response...")
    return handler.prompt(prompt).text()

if __name__ == "__main__":
    config = getcfg()
    model = llm.get_model(config["answermodel"])
    conversation = model.conversation()
    while True:
        userinput = input(">>> ")
        if config["timestamp"]=="yes":
            print(time.strftime("[%H:%M:%S]"))
        response = interact(userinput, conversation)
        prefix = time.strftime("[%H:%M:%S] ") if config["timestamp"]=="yes" else ""
        print(prefix + response)