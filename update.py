#!/.venv/Scripts/python.exe

import llm
import json
import requests
import configparser
import sqlite_utils
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from colorama.ansi import clear_screen, Fore

def getcfg(filename: str="config.cfg") -> dict:
    cfgparser = configparser.RawConfigParser()
    cfgparser.read(filename)
    return dict(cfgparser.items("default"))

def clear():
    print(clear_screen(), end="")

def extractLinks(obj: BeautifulSoup, burl: str) -> list:
    """Extract Links from BeautifulSoup object"""
    internallinks = [a["href"] for a in obj.find_all("a", href=True)] # get link in href property
    internallinks = list(set([link for link in internallinks if link != "#"])) # remove empty hrefs and doubles
    internallinks = [link for link in internallinks if link.startswith("http") and link.startswith(burl) or not link.startswith("http")] # remove external links
    internallinks = [link if link.startswith("http") else burl+link for link in internallinks] # make links complete
    internallinks = [link for link in internallinks if not link.endswith("morgen.pdf") or not link.endswith("heute.pdf")] # filter password protected site
    internallinks = [link for link in internallinks if not ".." in link] # filter non accessible site
    return internallinks

def sitemap(url: str, verbose: bool=True) -> list:
    """Returns all interlinked (and publicly available) paths on the given website"""
    baseurl = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    globalURLs = [url]

    queue = [url]
    done = []
    while queue:
        curURL = queue[-1]
        html = requests.get(url).content
        parsed = BeautifulSoup(html, "html.parser")
        intLinks = extractLinks(parsed, baseurl)
        globalURLs += [link for link in intLinks if link not in globalURLs]
        done.append(curURL)
        queue[:0] = [link for link in intLinks if link not in queue and link not in done]
        queue.pop(-1)
        if verbose:
            print(f"{Fore.LIGHTRED_EX}Queue: {str(len(queue)).zfill(3)}{Fore.WHITE} | {Fore.LIGHTGREEN_EX}Done: {str(len(done)).zfill(3)}{Fore.WHITE} | {Fore.LIGHTCYAN_EX}Global: {str(len(globalURLs)).zfill(3)}{Fore.WHITE} | {Fore.WHITE + curURL}")
    globalURLs.sort()
    return globalURLs

def extractText(links: list[str], verbose: bool=True) -> list:
    """Extracts the content of all text elements of every site in `links`"""
    result = []
    htmlcontents = []
    for ix, url in enumerate(links):
        html = requests.get(url).content
        if html in htmlcontents:
            continue
        htmlcontents.append(html)
        parsed = BeautifulSoup(html, "html.parser")
        p_tags = parsed.find_all("p")
        for p in p_tags:
            for br in p.find_all("br"):
                br.replace_with("###")
        result.append({"id": ix, "content": "###".join(p.text.strip() for p in p_tags).replace(" ", " ").replace("######", "###")}) # first replacement is no breaking space U+00A0
        if verbose:
            print(Fore.RED + f"[{str(ix).zfill(len(str(len(links))))}]" + Fore.WHITE + " | " + Fore.WHITE + "/".join(url.split("/")[:-1]) + Fore.LIGHTCYAN_EX + f"/{url.split('/')[-1]}" + Fore.WHITE)
    return [{"id": d["id"], "content": d["content"][3:] if d["content"].startswith("###") else d["content"][:-3] if d["content"].endswith("###") else d["content"]} for d in result if d["content"] != ""]

def updateData(path: str, url: str, verbose: bool=True):
    if verbose:
        print(Fore.WHITE + "Mapping Website...")
    sitelist = sitemap(url, verbose)
    clear()
    if verbose:
        print(Fore.WHITE + "Extracting Text...")
    text = extractText(sitelist, verbose)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(text, f, indent=4, ensure_ascii=False)

def updateDB(datapath: str, dbpath: str, modelname: str, verbose: bool=True):
    if verbose:
        print("Create Database...")
    db = sqlite_utils.Database(dbpath, recreate=True)
    embeddingmodel = llm.get_embedding_model(modelname)
    collection = llm.Collection("default", db, model=embeddingmodel)
    if verbose:
        print("Load Data from file...")
    with open(datapath, "r") as f:
        data = json.load(f)
    if verbose:
        print("Prepare Data...")
    data = [(str(item["id"]), item["content"]) for item in data]
    if verbose:
        print("Creating embedding vectors...")
    collection.embed_multi(data)

if __name__ == "__main__":
    config = getcfg()
    updateData("data.json", config["website"])
    clear()
    updateDB("data.json", "embeddings.db", config["embeddingmodel"])