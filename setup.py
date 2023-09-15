import os # preinstalled
import venv # preinstalled
import configparser # preinstalled

requirements = ["llm", "colorama", "bs4", "requests", "urllib3", "langchain"]

if not os.path.exists(".venv"):
    venv.create(".venv", with_pip=True)
if os.name == "nt":
    vpython = ".venv/Scripts/python.exe"
else:
    vpython = ".venv/bin/python3"
prefix = vpython + " -m "

os.system(prefix + "pip install " + " ".join(requirements))

os.system(prefix + "llm install llm-gpt4all llm-sentence-transformers")

os.system(prefix + "llm sentence-transformers register multi-qa-mpnet-base-dot-v1")

config = configparser.ConfigParser()
config["default"] = {"website": "https://example.com",
                    "embeddingmodel": "sentence-transformers/multi-qa-mpnet-base-dot-v1",
                    "answermodel": "wizardlm-13b-v1",
                    "singlestore": "yes",
                    "similarnum": 5,
                    "timestamp": "no"}
config["ignoreendings"] = {"ending1": "pwprotected.pdf",
                           "ending2": "someother.html"}
with open("config.cfg", "w") as f:
    config.write(f)