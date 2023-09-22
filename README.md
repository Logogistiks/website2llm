# Website2llm
Maps all the publicly availabe pages that link to each other on a webserver based on a given starting url, then scrapes all the contents into a database so the user can retreive information about the webpages through an [EM](https://en.wikipedia.org/wiki/Word_embedding) and [LLM](https://en.wikipedia.org/wiki/Large_language_model).

> Note: The prompt template used for feeding the LLM is currently in german, if you want to change it or add aditional instructions, simply edit `main.py` and change the template function in the main section.

![Workflow](/images/website2llm_workflow.svg)

![Process](/images/visualisation.png)

## Prequisites
* Python3
* pip
* git

## Installation
Clone the repo with this command:
```
git clone https://github.com/Logogistiks/website2llm
```
Then cd into the folder:
```
cd website2llm
```
Then just run `setup.py`. As you can see in the diagram above, it creates a virtual environment, installs all its requirements and creates a template config file.

## Configuration
Edit `config.cfg`. Things you can specify in the default category:
| Parameter        | Description                                                           | Possible Values                                                                            |
|------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------------------------------|
| `website`        | Link to a page on the webserver you want to scrape                    |                                                                                            |
| `embeddingmodel` | The embedding model used for converting sentences to vectors          | List of available models: https://www.sbert.net/docs/pretrained_models.html#model-overview |
| `answermodel`    | The model used for answering the question of the user                 | List of available models: https://observablehq.com/@simonw/gpt4all-models                  |
| `singlestore`    | Whether to store every `<p>` tag into a single DB entry or a whole page | `yes` <> `no`                                                                              |
| `similarnum`     | The number of DB entries used to generate the answer                  |                                                                                            |
| `timestamp`      | Whether to print a timestamp before and after interacting with the LM | `yes` <> `no`                                                                              |

> (Optional) \
Entering something into the ignoreendings category ignores sites with the specified endings while scraping, e.g. for sites that are password protected or you simply don't want

## Usage
Please make sure to edit the config file first, as described above.
### Updating
To update the database, run `update.py` with the python interpreter from the venv (on Windows: `.venv\Scripts\python.exe` ; on Linux: `.venv/bin/python3`). Updating is required if the website you scraped last was updated or if you want to scrape a new one. For the latter, make sure to update the config file.

The process is verbose by default, if you don't want any output (not recommended), you can edit `update.py` and add the `verbose=False` parameter to the `updateData()` and `updateDB()` function calls in the main section.

The creation of the embedding vectors can take some time, especially if the webserver contains a lot if sites, so please be patient.

### Information retrieval
Simply run `main.py` using the interpreter  as specified above, type in your question about the website and wait for the response. Please note that this process can take a lot of time, during my testing up to a full minute.

# Disclaimer
This project is very `experimental`, it is more of a concept than a serious tool. I just wanted to see if something like this is possible. The answer is yes, but very very slowly. \
I admit that the code of this project is garbage, but this was thrown together in about 3 weeks. \
I don't know if, what or how much improvements are coming in the future, but i plan to somehow make this conversation friendly, so you can chat with it like a real chat model. \
Please be patient, the embedding- or answer-generating- process may take a lot of time.

Warning: If the website is really big (it has many webpages), the amount of data collected can get relatively big (under `10MB` during testing with a website consisting of `~100 pages`). \
Also, im not responsible for the network traffic and the possible consequences that may occur. During my testing, the `traffic` was relatively low, with a peak of `~1KB per second`. \
But please inform yourself about the rules concerning webscraping tools on the target websites, im not responsible for your actions.

# References
LLM Python API: https://llm.datasette.io/en/stable/

Embedding model: https://github.com/simonw/llm-sentence-transformers

Answer model: https://github.com/simonw/llm-gpt4all

Graph Software for readme-Image: https://www.yworks.com/products/yed

Markdown table generator: https://www.tablesgenerator.com/markdown_tables
