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
> Note :- "If you are using **pip** method to install modules, then also you have to run the second command to install necessary **nltk** libraries"
- After installation of all necessary *modules* and *libraries*.
    - Write your "**Bearer-Token**" in `/resources/config.json` . like : -
    ```json
    {
	    "Bearer Token": "<ADD HERE YOUR BEARER TOKEN>"
    }
    ```
> There are **2** way to authenticate to **Twitter API**. One is via using **Bearer Token** only  and Another is  via **Consumer key , Consumer Secret Key, Access Token & Access Secret Token**.
    
> Both have major difference in term of **Rate limits** on `Tweets Search` . **Bearer Token** having upper hand with *450 requests per 15 minutes*. [Details here](https://developer.twitter.com/en/docs/twitter-api/rate-limits)
---
### Get Bearer Token, How?
Steps to get Bearer token *( Via **twitter** docs )* : -
-   Approved Twitter developer account (if you don’t have one, you can  [apply for access](https://developer.twitter.com/en/apply-for-access)).
    
-   A Twitter  [developer App](https://developer.twitter.com/en/docs/apps). You can create a new developer App or access existing ones in the  [Projects & Apps section](https://developer.twitter.com/en/portal/projects-and-apps)  of your developer account.

### HELP MENU
```
usage: pysmscraper.py [-h] [-k KEYWORD] [-m MAX RESULTS] [-t THREADS] [-p [OPTIONAL]] [-f [OPTIONAL]] [-o CSV FILE PATH] [-y [OPTIONAL]] [--silent [OPTIONAL]] [--install [REQUIRED ONCE]]

A Social media Scrapper tool for specifically Twitter to measure reponses of a particular keyword

options:
  -h, --help            show this help message and exit
  -k KEYWORD, --keyword KEYWORD
                        Keyword to search.
  -m MAX RESULTS, --maxresult MAX RESULTS
                        How many tweets, want to scan? (default - 10)
  -t THREADS, --threads THREADS
                        Maximum Threads to allow, (default - auto, "but less_than 100")
  -p [OPTIONAL], --progress [OPTIONAL]
                        Show progress of tweets fetching. (default - "FALSE")
  -f [OPTIONAL], --fast [OPTIONAL]
                        Need Tweets Fast? (It takes less time than normal but not sure to gather demanded max_results) (default - "FALSE")
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
    python pysmscraper.py -k "google" -m 1000 --silent -f -p -o google_tweets.csv

Note:
    * By default, The tool run on Normal pace mode. So High chance that you will recv your desired max_result tweets.
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
---
### Sample Video :-

https://user-images.githubusercontent.com/86392841/161448496-df7fa0ef-5af3-487c-b5c2-fb958485f8a4.mp4

---
### NOTES
- If you are using it on *linux* or *mac* and You receive **warnings** like this :- 
```sh
(process:2394): Gtk-WARNING **: 15:48:28.568: Theme parser error: gtk.css:4403:12-17: "shade" is not a valid color name.
```
then Ignore this, It's just because of **matplotlib colors**.

- `resources/words_dict.json` is from [dwyl repo](https://github.com/dwyl/english-words) .

---
### TODO
    - Use many more social media platforms like twitter for the work
    - Use less request for uniq tweets
    - Change name of Uniq mode as per characterstics


