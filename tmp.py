from os.path import basename, normpath
import configparser
def getcfg(filename: str="config.cfg", section: str="default") -> dict:
    """Load config properties from config file"""
    cfgparser = configparser.RawConfigParser()
    cfgparser.read(filename)
    return dict(cfgparser.items(section))
burl = "https://example.com"
internallinks = ["https://example.com/test",
                 "https://example.com/test/",
                 "https://example.com/test?abc=123",
                 "https://example.com/test/?abc=123&def=456",
                 "https://google.com",
                 "https://google.com/?abc=123",
                 "/fragment",
                 "/fragment/",
                 "/fragment?abc=123",
                 "/fragment/?abc=123",
                 "mailto:hans@peter.net",
                 "https://example.com/jquery=MyFunc(xdhaha);",
                 "/picture.png",
                 "/picture2.JPEG",
                 "/fragment/site.php",
                 "fragwoslash",
                 "fragwoslash2.pdf",
                 "/frag#anchor"]

complete = lambda u, bu: u if u.startswith(bu) else bu+u # complete url fragments to full links
norm = lambda u: basename(normpath(u[:u.find("?")] if "?" in u else u)) # remove query parameters and return last part of url path, aka. "the part after the last slash"

isplaceholder = lambda u: u.strip() == "#" # link can not be placeholder value
isexternal = lambda u, bu: not u.startswith(bu) and not u.startswith("/") # link must be from the current domain
isunwanted = lambda u: any(sub in u for sub in ["..", "mailto:", "tel:", "(", ")", ",", "/termine/", "/jevents"]) # link can not contain these impurities
isextrafile = lambda u, bu: "." in norm(complete(u, bu)) and not any(norm(complete(u, bu)).endswith(end) for end in ["html", "php"]) # link must be a webpage, not a file / document
isignored = lambda u: any(u.lower().endswith(ignore.lower()) for ignore in getcfg(section="ignoreendings").values()) # check if link is marked as ignored in the config.cfg

extracted = [complete(link, burl) for link in internallinks if not any([isplaceholder(link), isexternal(link, burl), isunwanted(link), isextrafile(link, burl), isignored(link)])]
"""new = []
for link in internallinks:
    if any([isplaceholder(link), isexternal(link, burl), isunwanted(link), isextrafile(link, burl), isignored(link)]):
        continue
    new.append(complete(link, burl))"""

"""new = []
for link in internallinks:
    if link.strip() == "#":
        continue
    if not link.startswith(burl) and not link.startswith("/"):
        continue
    if any(sub in link for sub in ["..", "mailto:", "tel:", "(", ")", ",", "/termine/", "/jevents"]):
        continue
    clink = link if link.startswith(burl) else burl+link # complete link
    blink = norm(clink) # base link
    if "." in blink and not any(blink.endswith(end) for end in ["html", "php"]):
        continue
    if any(link.lower().endswith(ignore.lower()) for ignore in getcfg(section="ignoreendings").values()):
        continue

    new.append(clink)"""

for n in new:
    print(n)