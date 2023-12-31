import llm
import json
import requests
import configparser
import sqlite_utils
from uuid import uuid4
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from os.path import basename, normpath
from colorama.ansi import clear_screen, Fore

def remquery(u):
    return basename(normpath(u[:u.find("?")] if "?" in u else u))

def getcfg(filename: str="config.cfg", section: str="default") -> dict:
    """Load config properties from config file"""
    cfgparser = configparser.RawConfigParser()
    cfgparser.read(filename)
    return dict(cfgparser.items(section))

def clear():
    """Clears screen via ansi sequence so content is not overwitten"""
    print(clear_screen(), end="")

def extractLinks(obj: BeautifulSoup, burl: str) -> list:
    """Extract Links from BeautifulSoup object"""
    # Define util functions
    complete = lambda u, bu: u if u.startswith(bu) else bu+u # complete url fragments to full links
    norm     = lambda u    : basename(normpath(u[:u.find("?")] if "?" in u else u)) # remove query parameters and return last part of url path, aka. "the part after the last slash"

    # Get User-Criteria
    user_ignore_ends = list(getcfg(section="ignoreendings").values())
    user_ignore_imp = list(getcfg(section="ignoreimpure").values())

    # Define Anti-Criteria
    isplaceholder = lambda u    : u.strip() == "#" # link can not be placeholder value
    isexternal    = lambda u, bu: not u.startswith(bu) and not u.startswith("/") # link must be from the current domain
    isunwanted    = lambda u    : any(sub in u for sub in ["..", "mailto:", "tel:", "(", ")", ","]+user_ignore_imp) # link can not contain these impurities
    isextrafile   = lambda u, bu: "." in norm(complete(u, bu)) and not any(norm(complete(u, bu)).endswith(end) for end in ["html", "php"]) # link must be a webpage, not a file / document
    isignored     = lambda u    : any(u.lower().endswith(ignore.lower()) for ignore in user_ignore_ends) # check if link is marked as ignored in the config.cfg

    # Check for Anti-Criteria
    linksonsite = [a["href"] for a in obj.find_all("a", href=True)] # get link in href property
    extracted = [complete(link, burl) for link in linksonsite if not any([isplaceholder(link), isexternal(link, burl), isunwanted(link), isextrafile(link, burl), isignored(link)])]
    return list(set(extracted)) # remove doubles

def sitemap(url: str, verbose: bool=True) -> tuple[list, dict]:
    """Returns all interlinked (and publicly available) paths on the given website"""
    baseurl = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    globalURLs = [url] # all scraped urls
    contentcache = {} # maps urls to its html code for later use to save bandwith
    queue = [url] # urls that are still to do
    done = [] # completed urls

    while queue:
        curURL = queue[-1]

        html = requests.get(curURL)
        contentcache[curURL] = html
        parsed = BeautifulSoup(html.content, "html.parser")

        internallinks = extractLinks(parsed, baseurl)

        globalURLs += [link for link in internallinks if link not in globalURLs] # add links to main list if not already present
        done.append(curURL)
        queue.extend([link for link in internallinks if link not in queue and link not in done]) # insert new links at start of queue
        queue.pop(0)

        if verbose: print(f"{Fore.LIGHTRED_EX}Queue: {str(len(queue)).zfill(3)}{Fore.WHITE} | {Fore.LIGHTGREEN_EX}Done: {str(len(done)).zfill(3)}{Fore.WHITE} | {Fore.LIGHTCYAN_EX}Global: {str(len(globalURLs)).zfill(3)}{Fore.WHITE} | {Fore.WHITE + curURL}")
    return (sorted(list(set(globalURLs))), contentcache)

def extractText(links: list[str], singlestore: bool, verbose: bool=True, contentcache: dict[str, requests.Response]=None) -> list:
    """Extracts the content of all text elements of every site in `links`"""
    result = []
    htmlremember = []

    for ix, url in enumerate(links):
        req = contentcache.get(url, None) if contentcache else requests.get(url) # retrieve html from mapping instead of making traffic
        if req is None or "pdf" in req.headers.get("Content-Type", ""):
            continue
        html = req.content
        if html in htmlremember:
            continue
        htmlremember.append(html)

        parsed = BeautifulSoup(html, "html.parser")
        p_tags = parsed.find_all("p")

        for p in p_tags:
            for br in p.find_all("br"):
                br.replace_with("###")
            if singlestore: result.append({"id": uuid4().hex, "content": p.text.strip().replace(" ", " ")}) # replace "no breaking space" U+00A0

        if not singlestore: result.append({"id": ix, "content": "###".join(p.text.strip() for p in p_tags).replace(" ", " ").replace("######", "###")})

        if verbose: print(Fore.RED + f"[{str(ix).zfill(len(str(len(links))))}]" + Fore.WHITE + " | " + Fore.WHITE + "/".join(url.split("/")[:-1]) + Fore.LIGHTCYAN_EX + f"/{url.split('/')[-1]}" + Fore.WHITE)
    return [d for d in result if d["content"] != ""]

def updateData(path: str, url: str, singlestore: bool, verbose: bool=True):
    """Update plain text database"""
    if verbose: print(Fore.WHITE + "Mapping Website...")
    sitelist, mapping = sitemap(url, verbose)

    clear()
    if verbose: print(Fore.WHITE + "Extracting Text...")
    text = extractText(sitelist, singlestore, verbose, contentcache=mapping)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(text, f, indent=4, ensure_ascii=False)

def updateDB(datapath: str, dbpath: str, modelname: str, verbose: bool=True):
    """Update the embedding database"""
    if verbose: print("Create Database...")
    db = sqlite_utils.Database(dbpath, recreate=True)
    embeddingmodel = llm.get_embedding_model(modelname)
    collection = llm.Collection("default", db, model=embeddingmodel)

    if verbose: print("Load Data from file...")
    with open(datapath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if verbose: print("Prepare Data...")
    data = [(str(item["id"]), item["content"]) for item in data]

    if verbose: print("Creating embedding vectors...")
    collection.embed_multi(data, store=True)

if __name__ == "__main__":
    config = getcfg()
    starttime = datetime.now()
    updateData("data.json", config["website"], config["singlestore"]=="yes")
    clear()
    updateDB("data.json", "embeddings.db", config["embeddingmodel"])
    endtime = datetime.now()
    elapsed = endtime - starttime
    if config["timestamp"]:
        print(f"{Fore.LIGHTGREEN_EX}Start time: {Fore.LIGHTYELLOW_EX}{starttime.strftime('%H:%M:%S')}, {Fore.LIGHTRED_EX}End time: {Fore.LIGHTYELLOW_EX}{endtime.strftime('%H:%M:%S')}, {Fore.LIGHTCYAN_EX}Elapsed: {Fore.LIGHTYELLOW_EX}{str(elapsed).split('.')[0]}" + Fore.WHITE)