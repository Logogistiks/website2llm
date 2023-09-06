import os # preinstalled
import venv # preinstalled
import configparser # preinstalled

requirements = ["llm", "colorama", "bs4", "requests", "urllib3", "langchain"]

venv.create(".venv", with_pip=True)
vpython = ".venv\\Scripts\\python.exe"
prefix = vpython + " -m "

os.system(prefix + "pip install " + " ".join(requirements))

os.system(prefix + "llm install llm-gpt4all llm-sentence-transformers")

os.system(prefix + "llm sentence-transformers register multi-qa-mpnet-base-dot-v1")

config = configparser.ConfigParser()
config["default"] = {"website": "https://example.com",
                    "embeddingmodel": "multi-qa-mpnet-base-dot-v1",
                    "answermodel": "wizardlm-13b-v1"}
with open("config.cfg", "w") as f:
    config.write(f)