## PySM Scraper

PySM Scraper is social media scraping tool made in `python3`. It help brand to discover their reputation on social media. It uses people public data [ like *tweets*, *comments*, etc.. ] to measure **brand's** reputation.

### Why PySM?
- Using [tweepy](https://www.tweepy.org/) module, with **Twitter API v2**
- Easy to Use, *cmdline utility*
- Packed with **threading** module, *fast speed*
- Using **NLTK**, *one of the best python NLP module*

### Installation
- You can install `PySM` easily with `git` command
```sh
git clone https://github.com/MAAYTHM/PySM.git
```

```sh
cd PySM
```

- Now for installing `required modules`. There are 2 ways :
```sh
pip install -r requirements.txt
```
OR
```sh
python3 pysmscraper.py --install
```

### Arguments
```
usage: pysmscraper.py [-h] [-k KEYWORD] [-m MAX RESULTS] [-t THREADS] [-p [OPTIONAL]] [-u [OPTIONAL]] [-o CSV FILE PATH] [-y [OPTIONAL]] [--silent [OPTIONAL]] [--install [REQUIRED ONCE]]

A Social media Scrapper tool for specifically Twitter to measure reponses of a particular keyword

options:
  -h, --help            show this help message and exit
  -k KEYWORD, --keyword KEYWORD
                        Keyword to search.
  -m MAX RESULTS, --maxresult MAX RESULTS
                        How many tweets, want to scan? (default - 10)
  -t THREADS, --threads THREADS
                        Maximum Threads to allow, (default - auto, " but less_than 500")
  -p [OPTIONAL], --progress [OPTIONAL]
                        Show progress of tweets fetching. (default - "FALSE")
  -u [OPTIONAL], --unique [OPTIONAL]
                        Need Unique Tweets? (It takes more time than normal) (default - "FALSE")
  -o CSV FILE PATH, --output CSV FILE PATH
                        File name to save results (.csv) (default - "scrapper_result.csv")
  -y [OPTIONAL], --yes [OPTIONAL]
                        If the program prompt for "yes"/"no", Then It will set "Yes" to each question (asked from the program) (default - FALSE)
  
  --silent [OPTIONAL]   Not print anything, ONLY errors will display and saving will be done. (default - FALSE)
  
  --install [REQUIRED ONCE]
                        Before running it first time for scraping, Use this flag to download all necessary nltk libraries

example: [ USE WITH PYTHON3 ]
    python pysmscraper.py -k "google"
    python pysmscraper.py --install
    python pysmscraper.py -k "google" -m 1000 --silent -p -o google_tweets.csv

Note:
    * By default, (without '-u' flag) The tool run on fast pace mode. So cannt gurrantee If u will recv your desired number of result. But yes, half of the desired result will be recvd.
    * "-u" flag will of the fast-pace mode. It will cost more number of requests.
    * Dont Panic If Tweets gathering's Progress bar showing less numbers of tweets comparing from prev progress. It will repair itself.

Made by (😎):
    * MAAY (https://github.com/MAAYTHM)
```

---
### Example Usage

```sh
python pysmscraper.py -k google
```
```sh
python pysmscraper.py -k google -m 1000 -p -u --silent -o google_tweets.csv
```

### TODO
    - Use many more social media platforms like twitter for the work
    - Use less request for uniq tweets
    - Change name of Uniq mode as per characterstics



