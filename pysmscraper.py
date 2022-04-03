## TO DO :-
    # use many more social media platforms like twitter for the work
    # Use less request for uniq tweets
    # Change name of Uniq mode as per characterstics

## Support links
# links - https://towardsdatascience.com/calculating-the-semantic-brand-score-with-python-3f94fb8372a6


# For making cmd line functionality tool
from argparse import ArgumentParser as AP, RawDescriptionHelpFormatter

# For system cmds, exit
import os
import sys
import subprocess

# To Calculate time 
import time

## For threading work
from threading import Thread, active_count, Event
import signal

# For support work
import json
import re
import string
from collections import Counter


########################################################################### IMPORT END


########################################################################### Classes & Functions

class Gather_tweets(object):

    def __init__(self):
        global unique, keyword

        ## General Class variables
        self.url = 'https://api.twitter.com/2/tweets/search/recent'
        
        ## Global Class variables
        self.allow_uniq = unique
        self.keyword = keyword
        self.show_progress = show_progress


    def gather_tweepy(self, client, max_results, limit, next_token, tweets_list, tweets_dict, temp_goal, Total_count):
        global exit_event, delimiter, Total_requests


        ## Local function variables
        query = f'("{self.keyword}" OR "{self.keyword.upper()}" OR "{self.keyword.capitalize()}") lang:en has:mentions -is:retweet'
        function_count = 0 
        break_flag = False
        local_delimiter = " " + delimiter + " "


        ## rechecking "max_results" parameter value
        if max_results <= 10: max_results = 10

        ## Function's Main loop
        for i in range(limit):

            if Total_requests == Twitter_rate_limit_rq:
                error_display(desc = "\tTwitter Rate limit reached, Retry After 15 minutes - \n[ info ] Processing tweets which we gathered till", exit=False)
                break_flag = True

            ## If any error occurs while connecting to twitter API
            try:
                response = client.search_recent_tweets(query = query, max_results = max_results, next_token = next_token)
                Total_requests += 1
            
            except Exception as error:
                error_display(desc = f"Invalid Bearer Token OR Something different happened !! ", error = error)

            next_token = response.meta["next_token"]

            for tweet in response.data:
                
                ## Checking If Ctrl+c is already pressed?
                if exit_event.is_set(): sys.exit()

                ## Getting "text" from "data" dict
                tweet = tweet.text

                ## Checking duplicate tweet (small duplicate check)
                if tweet not in tweets_list:
                    
                    ## Appending tweets to tweets list
                    tweets_list.append(tweet)

                    if not self.allow_uniq:

                        ## increasing function count without checking length , if "-u" is not set
                        function_count += 1

                        ## Showing Progress (without "-u") :-
                        if self.show_progress: custom_print(f"\t\tTweets gathered - {Total_count + function_count} tweets", end='\r')
                        
                        ## If goal achieved in mid of checking tweets, then exit
                        if temp_goal == function_count: break_flag = True;break
            

            ## if "-u" is given
            if self.allow_uniq:
                
                ## Converting "tweets" list into single string
                delimiter_tweets = local_delimiter.join(tweets_list)
                supporter = support_Purify()
                pure_tweets = supporter.clear_tweet(tweet = delimiter_tweets).split(local_delimiter)

                ## Appending tweets to tweets dict
                for index, pure_tweet in enumerate(pure_tweets):

                    ## removing duplicates
                    if pure_tweet not in tweets_dict:
                        tweets_dict[pure_tweet] = [tweets_list[index], "none"]
                        function_count += 1
                    
                    ## Showing Progress (with "-u") :-
                    if self.show_progress: custom_print(f"\t\tTweets gathered - {Total_count + function_count} tweets", end='\r')

                    ## If goal achieved in mid of checking tweets, then exit
                    if temp_goal == function_count: break

            
            ## Waiting for acheiving "temp_goal"
            if break_flag: break
        
        ## Returning How many uniq tweets we gathered in this function
        return function_count, next_token



class Purifier(Thread):
    def __init__(self, tweets_list, tweets_dict):
        global exit_event, break_event

        Thread.__init__(self)
        self.original_tweets = tweets_list
        self.tweets_dict = tweets_dict

        ## Global Variable
        self.break_event = break_event
        self.exit_event = exit_event

    def run(self):

        while True:

            ## If there is anything in the list remaning then , try condition will work
            try:
                tweet = self.original_tweets.pop()
            except:
                if not self.break_event.is_set(): self.break_event.set()
                break

            ## Purifying Tweet
            pure_tweet = support_Purify().clear_tweet(tweet=tweet)

            ## if 'Ctrl+C' is pressed
            if self.exit_event.is_set(): break

            ## Replacing
            self.tweets_dict[pure_tweet] = [tweet, 'none']



class support_Purify():
    
    def __init__(self):
        global delimiter
        
        self.delimiter = delimiter

    ## Function
    def clear_tweet(self, tweet):
        global pattern_punctuation, pattern_stopwords, keyword, pos_dict, word_lemmatizer, unique

        new_text = tweet

        ## Step - Removing @names
        new_text = re.sub(r"@\S+", " ", new_text)

        ## Step - Removing https://links and www.links
        new_text = re.sub(r"http\S+", " ", new_text)
        new_text = re.sub(r"www\S+", " ", new_text)

        ## Step - Replacing HTML Entities like - '&amp;', '&quot;' etc..
        new_text = str(replace_entities(new_text))

        ## Step - Removing Punctuations
        new_text = pattern_punctuation.sub(' ', new_text)

        ## Step - Removing Stopwords
        new_text = pattern_stopwords.sub(' ', new_text)

        ## Step - COnverting emojis to text
        new_text = self.emojis_to_text(new_text)
        
        ## Step - Correcting [ words from text ]
        new_text = self.spell_corrector(new_text)

        ## Step - Extra Spaces
        new_text = re.sub(' +', ' ', new_text)

        ## Step - Lemmatizing each word else of keyword with POST(Parts Of Speech Tagging)
        new_text = new_text.split()
        pos_data = nltk.pos_tag(new_text)
        temp_var, space_var = "", 0

        for word, pos in pos_data:
            if temp_var: space_var = 1
            if word.lower() == keyword or (unique and word == self.delimiter): " "*space_var + word
            try:
                pos = pos_dict[pos[0]]
                lemma = word_lemmatizer.lemmatize(word)
                temp_var += " "*space_var + lemma
            except: temp_var += " "*space_var + word
        new_text = temp_var

        return new_text


    ## Function
    def spell_corrector(self, tweet):
        global WORDS, keyword, unique

        def probability(word, N=sum(WORDS.values())):
            " Probability of word occurence in WORDS dict. "
            return WORDS[word] / N

        def correction(word):
            " Most probable spelling correction for word. "
            return max(candidates(word), key=probability)

        def candidates(word):
            " Generate possible spelling corrections for word. "
            return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

        def known(words):
            " The subset of `words` that appear in dict of WORDS. "
            return set(w for w in words if w in WORDS)

        def edits1(word):
            " All edits that are one edit away from `word`. "
            letters = "abcdefghijklmnopqrstuvwxyz"
            splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
            deletes = [L + R[1:] for L, R in splits if R]
            transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
            replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
            inserts = [L + c + R for L, R in splits if R for c in letters]

            return set(deletes + transposes + replaces + inserts)

        def edits2(word):
            " All edits that are two edits away from `word`. "
            return (e2 for e1 in edits1(word) for e2 in edits1(e1))
        
        
        list_ofwords = re.findall("\w+", tweet)
        new_text = ''
        for word in list_ofwords:
            if not unique or (unique and word != self.delimiter):
                word = re.sub('_', '', word.lower())
                if word and not word.isdigit() and word != keyword:
                    word = correction(word)
            new_text += word + " "

        return new_text
    
    
    ## Converting each emojis into proper word
    def emojis_to_text(self, text):
        dict_of_emojis = demoji.findall(text)

        ## If found any emoji in word, like -> '♾️loop'
        if dict_of_emojis:
            for emoji, meaning in dict_of_emojis.items():
                text = text.replace(emoji, meaning)
        return text



class Analyser(Thread):
    def __init__(self, tweets_dict, tweets, analyzer):
        global exit_event, break_event

        Thread.__init__(self)
        self.tweets_dict = tweets_dict
        self.tweets = tweets
        self.analysis = analyzer

        ## Global Variable
        self.exit_event = exit_event
        self.break_event = break_event

    def run(self):

        ## Running ♾️loop, which will break when there's nothing in tweets list
        while True:
            try:
                tweet = self.tweets.pop()
            except:
                if not self.break_event.is_set(): self.break_event.set()
                break

            ## if 'Ctrl+C' is pressed
            if self.exit_event.is_set(): break

            ## Calculating sentiments
            sentiment = self.which_sentiment(tweet)

            ## Updating sentiments for respected tweets
            self.tweets_dict[tweet][1] = sentiment

    ## Analysing Sentiments
    def which_sentiment(self, tweet):

        ## Using SIA (Sentiment Intensity Analyzer) class here
        value_dict = self.analysis.polarity_scores(tweet)
        max_value = max(value_dict, key=value_dict.get)
        
        ## Checking Sentiment - '+ve', '-ve' or 'n'
        if max_value == 'pos' or (max_value == 'compound' and value_dict[max_value] >= 0.5): return '+ve'
        elif max_value == 'neg' or (max_value == 'compound' and value_dict[max_value] <= -0.5): return '+ve'
        else: return 'n'




## CUstom print function , for handling "--silent" flag
def custom_print(*args, **kwargs):
    global silent

    ## local variables
    print_data = ""

    ## Getting values from parameters
    for items in args:
        print_data += str(items)
    end = kwargs.get("end")
    error = kwargs.get("error")

    ## Print all If "--silent" flag is not used
    if not silent and not exit_event.is_set(): print(print_data, end=end)

    ## If any error occur then print it, even with "--silent" flag
    elif error: print(print_data, end=end)


def clear_screen():
    ## Clearing screen/terminal for Windows
    if os.name == 'nt':
        os.system('cls')
    
    ## Clearing screen for Linux/BSD/Mac
    else:
        os.system('clear')


def main():
    global keyword, max_results, output_filename, max_threads, show_progress, silent, unique, all_yes, token


    ## general variable
    All_uniq_tweets = {} # format -> {"pure_tweet": ["original_tweet", "sentiment"]}
    Original_tweets = []
    Total_count = 0

    ## Declaring "no_of_threads", not more than max_threads
    if max_threads == None:
        no_of_threads = length = max_results
        max_threads = 500
        
        if length == 100: no_of_threads = 25
        elif 15 >= length: pass
        elif length < 100: no_of_threads = 15
        else: no_of_threads = (length // 2)
        
        ## If "no_of_threads" exceeds default "max_threads" limit
        if no_of_threads > max_threads: no_of_threads = max_threads
    
    ## If user assigned it, then take that
    else: 
        no_of_threads = max_threads
    
    ## Creating signal for 'Ctrl+C' & for handling 'Ctrl+C' Interruption
    signal.signal(signal.SIGINT, signal_handler)

    ## Printing the Input & Notice
    if not silent:
        custom_print("#"*10, " INFO BANNER ", "#"*10)
        custom_print(f"Keyword (-k) - '{keyword}'")
        custom_print(f"Max Results (-m) - {max_results} tweets")
        custom_print(f"Output FileName (-o) - '{output_filename}'")
        custom_print(f"Progress Shown (-p) - {show_progress}")
        custom_print(f"Max Threads Allowed (-x) - {no_of_threads} (based on allowed Max results, Max threads and some Calculation)")
        custom_print(f"Unique Tweets (-u) - {unique}")
        custom_print(f"All Answer 'Yes' (-y) - {all_yes}")
        custom_print("#"*10, " INFO BANNER ", "#"*10)
        custom_print()

    ## STEP 1 -> "Gathering Uniq Tweets"
    Step_1(total_results = max_results, Original_tweets = Original_tweets, All_uniq_tweets = All_uniq_tweets, Total_count = Total_count)

    ## STEP 2 -> "Threading For Puryfying Tweets"
    if not unique: Step_2(Original_tweets = Original_tweets, All_uniq_tweets = All_uniq_tweets, no_of_threads = no_of_threads)

    ## STEP 3 -> "Threading For Sentiment Analyzing"
    Step_3(All_uniq_tweets = All_uniq_tweets, no_of_threads = no_of_threads)

    ## showing How much request send to twitter, for collecting tweets
    custom_print(f"Total_requests -> {Total_requests} requests")

    ## new lines for format printing
    time.sleep(1)
    clear_screen()
    custom_print()
    custom_print("#"*10, " Showing & Saving Result ", "#"*10)
    calculate_results(tweets_dict = All_uniq_tweets)



## STEP 1 -> "Gathering Uniq Tweets"
def Step_1(total_results, Original_tweets, All_uniq_tweets, Total_count):
    global exit_event, unique, token, Total_requests, Twitter_rate_limit_min, Twitter_rate_limit_rq

    if unique: custom_print(f"Step 1 - Gathering & Purifying Tweets (Started)")
    else: custom_print(f"Step 1 - Gathering Tweets (Started)")

    ## variables from main() function
    Remaining_result = total_results

    ## Local function variables
    Twitter_search_limit = Twitter_rate_limit_rq * 100 # 450 * 100 -> 45,000 tweets can gather in 15 min.
    Twitter_wait_time = Twitter_rate_limit_min * 60 # 15 mins in seconds -> 900 sec
    Next_token = None
    Client = tweepy.Client(bearer_token=token)
    Gatherer = Gather_tweets()
    
    ## Calculating "Total_time_taking" via "total_results"
    Total_time_taking = 0
    Total_time_taking += total_results // 100
    
    ## If user want result which is not divisible by 100 perfectly like 129, 1, etc..
    if (total_results % 100): Total_time_taking += 1
    
    ## FOr if "-u" set, becoz of the "support_Purify" CLass
    if unique: Total_time_taking = total_results // 3


    ## Displaying Info Banners
    custom_print(f"\t[!] According to Twitter API docs, Rate Limit (Over Search Tweets) is {Twitter_rate_limit_rq} requests / {Twitter_rate_limit_min} min.")
    custom_print("\t[!] means, This Tool can only gather around 44.5k tweets per 15 minutes.")
    custom_print(f"\tMax time to gather ({total_results} tweets) -> {Total_time_taking} sec")
    custom_print()
    if show_progress: custom_print("\tProgress INFO :-")

    ## MAIN LOOP :-
    start = time.time()
    while Remaining_result != 0:

        ## Checking for Ctrl+c pressed?
        if exit_event.is_set():
            sys.exit(f"(Step 1) Time taken :- {time.time() - start}")

        ## "temp_limit" is simillar to "remaining_result", only diff is -> "temp_limit" is a local variable for this loop where "remaining_result" is a global variable
        temp_limit = Remaining_result % Twitter_search_limit

        ## for handling if "remaining_result" == "45000"
        if Remaining_result >= Twitter_search_limit: temp_limit = Twitter_search_limit

        ## updating "remaining_result"
        Remaining_result -= temp_limit

        ## setting "temp_goal" variable for this loop
        temp_goal = temp_limit
        temp_goal_achieved = 0

        ## declaring & initializing "max_results", "extra_results" & "local_time_taking" variable
        ## "max_results" -> max tweets, we are allowed to fetch in 1 request.
        ## "extra_results" -> 2 digit no_of_requests out of big "no_of_requests". like 11 out of 1011, 10 outof 1010, 1 outof 101. Not 2 digit request like 89, 12, 45 etc ...
        max_results = 100
        extra_results = temp_limit % 100
        if temp_limit < 10: extra_results = 10

        ## changing "extra_results" to 100, if "-u" flag is set. else "-u" cost very high in total number of request
        if unique and extra_results: extra_results = 100

        ## calculating pages needed to surf (twitter API Tweets pages with 'next_token') , via "temp_limit" variable. Only for those no. of request which is divisible by 100 and remainder is "0".
        no_of_pages = temp_limit // 100

        ## Checking "Total_requests" > "Twitter_rate_limit_rq" so that in bw function loop, no error occur, part - 1
        if Total_requests > Twitter_rate_limit_rq:
            ## format printing
            if show_progress: custom_print()

            error_display(desc = "\tTwitter Rate limit reached, Retry After 15 minutes - \n[ info ] Processing tweets which we gathered till", exit=False)
            break

        ## calling main function & Updating "temp_goal_achieved" according to results achieved
        if no_of_pages:
            temp_1, Next_token = Gatherer.gather_tweepy(client=Client, max_results=max_results, limit=no_of_pages, next_token=Next_token, tweets_list=Original_tweets, tweets_dict=All_uniq_tweets, temp_goal=temp_goal, Total_count=Total_count)
            temp_goal_achieved += temp_1
        if extra_results:
            temp_1, Next_token = Gatherer.gather_tweepy(client=Client, max_results=extra_results, limit=1, next_token=Next_token, tweets_list=Original_tweets, tweets_dict=All_uniq_tweets, temp_goal=temp_goal, Total_count=Total_count)
            temp_goal_achieved += temp_1
        
        ## Updating "total_count" variable by adding "temp_goal_achieved"
        Total_count += temp_goal_achieved

        ## Checking if "temp_goal_achieved" is not fulfilling "temp_goal"
        if temp_goal_achieved != temp_goal:
            Remaining_result += (temp_goal - temp_goal_achieved)

        ## waiting time per "Twitter_rate_limit_rq" requests, part - 2
        if Total_requests == Twitter_rate_limit_rq:
            ## format printing
            if show_progress: custom_print()

            error_display(desc = "\tTwitter Rate limit reached, Retry After 15 minutes - \n[ info ] Processing tweets which we gathered till", exit=False)
            break

    
    end_time = round((time.time() - start), 2)
    if show_progress: custom_print("\n")

    ## If Ctrl+c pressed already
    if exit_event.is_set():
        sys.exit(f"\t(Step 1) Time taken :- {end_time} sec")
    
    custom_print(f"\t(Step 1) Time taken :- {end_time} sec")
    custom_print()



## STEP 2 -> "Threading for Puryfying Tweets"
def Step_2(Original_tweets, All_uniq_tweets, no_of_threads):
    global exit_event

    ## a thread Start thread
    def start_threads(no_of_threads, Original_tweets, All_uniq_tweets, threads):
        global break_event

        ## variables for CLass parameters
        temp_original_tweets = [];temp_original_tweets.extend(Original_tweets)

        for _ in range(no_of_threads):
            if not break_event.is_set():
                thread = Purifier(tweets_list=temp_original_tweets, tweets_dict=All_uniq_tweets)
                threads.append(thread)
                thread.start()
            else: break

    ## local function var
    threads = []

    ## Timings
    start = time.time()
    custom_print(f"Step 2 - Purifying Tweets (Started)")
    custom_print(f"\tMax time to 'PURIFY' (6 tweets/sec) = {round((len(Original_tweets) // 6), 2)} sec. (Depend On number of 'threads and tweets')")
    custom_print()
    
    ## Starting all threads with a thread
    starting_thread = Thread(target = start_threads, kwargs={"no_of_threads": no_of_threads, "Original_tweets": Original_tweets, "All_uniq_tweets": All_uniq_tweets, "threads": threads})
    threads.append(starting_thread)
    starting_thread.start()

    ## Progress bar for threads
    lock()

    end_time = round((time.time() - start), 2)

    if exit_event.is_set(): sys.exit(f"\t(Step 2) Time taken :- {end_time} sec")
    custom_print(f"\t(Step 2) Time taken :- {end_time} sec")
    custom_print()



## Threading for Sentiment Analyzing
def Step_3(All_uniq_tweets, no_of_threads):
    global exit_event

    ## a thread Start threads
    def start_threads(no_of_threads, All_uniq_tweets, threads):
        global break_event

        ## If break event triggered by Step 2, then reset it in Step 3
        if break_event.is_set(): break_event.clear()

        ## variable to pass on to CLass
        tweets = list(All_uniq_tweets.keys())
        analyzer = SentimentIntensityAnalyzer()

        ## Declaring & Initializing threads
        for _ in range(no_of_threads):
            if not break_event.is_set():
                thread = Analyser(tweets_dict=All_uniq_tweets, tweets=tweets, analyzer=analyzer)
                threads.append(thread)
                thread.start()
            else: break
        
        ## If break event triggered by Step 3, then reset it
        if break_event.is_set(): break_event.clear()


    ## local func variables
    threads = []

    ## Timings
    start = time.time()
    total_time = round(((len(All_uniq_tweets) // 100) * 2), 2)
    if not total_time: total_time = 1.0

    custom_print(f"Step 3 - Sentiment Analysing (Started)")
    custom_print(f"\tMax time to 'PURIFY' (({len(All_uniq_tweets)} tweets / 100) x 2) = {total_time} sec")
    custom_print()
    
    ## starting_thread for starting other threads
    starting_thread = Thread(target = start_threads, kwargs = {"no_of_threads": no_of_threads, "All_uniq_tweets": All_uniq_tweets, "threads": threads})
    threads.append(starting_thread)
    starting_thread.start()

    ## Main thread will go to loop till other threads are doing work
    lock()

    end_time = round((time.time() - start), 2)
    
    if exit_event.is_set(): sys.exit(f"\t(Step 3) Time taken :- {end_time} sec")
    custom_print(f"\t(Step 3) Time taken :- {end_time} sec")
    custom_print()



## Calculating results from 'tweets_dict'
def calculate_results(tweets_dict):
    global exit_event, keyword, output_filename

    purified_tweets = list(tweets_dict.keys())
    responses = []
    original_tweets = []
    tweets = []

    ## Checking If ctrl+c already pressed
    if exit_event.is_set(): sys.exit()

    for key,values in tweets_dict.items():
        responses.append(values[1]);original_tweets.append(values[0])
        tweets.append([values[0], key])
    keyword = keyword.capitalize()
    positive_count = responses.count('+ve')
    negative_count = responses.count('-ve')
    neutral_count = len(tweets_dict) - (positive_count + negative_count)

    ## Checking If ctrl+c already pressed
    if exit_event.is_set(): sys.exit()

    ## Saving tweets in ".csv" file, if user provided "output_file" name
    if output_filename:
        response_name_dict = {"+ve":"Positive Response", "-ve":"Negative Response", "n": "Neutral Response"}
        tweets_df = pd.DataFrame(tweets, index=[response_name_dict[response] for response in responses], columns=['Original Tweets', 'Purified Tweets'])
        try:
            tweets_df.to_csv(output_filename)
            custom_print()
            custom_print(f"[+] Saved to '{output_filename}' file")
        except Exception as error: error_display(desc = f"Error while saving in file ({output_filename}), ", error=error, exit = False)


    ## Checking If ctrl+c already pressed
    if exit_event.is_set(): sys.exit()

    ## Printing -ve responses :-
    if negative_count:
        custom_print()
        custom_print("-: Negative Tweets :-")

        while responses.count('-ve'):
            index = responses.index()
            tweet = purified_tweets.pop(index)
            responses.remove('-ve')
            custom_print(f"{negative_count - responses.count('-ve')}) ", tweet)

    ## Checking If ctrl+c already pressed
    if exit_event.is_set(): sys.exit()
    custom_print()
    custom_print(f"Postive Responses - {round((positive_count/len(tweets_dict))*100, 2)}% / 100%")
    custom_print(f"Negative Responses - {round((negative_count/len(tweets_dict))*100, 2)}% / 100%")
    custom_print(f"Neutral Responses - {round((neutral_count/len(tweets_dict))*100, 2)}% / 100%")
    custom_print()

    custom_print(f"\tAccording to Total({len(tweets_dict)}) Tweets Scanned :-")
    if (positive_count+neutral_count) > negative_count:
        custom_print(f"\t-> '{keyword}' has Nice Reputation. ({((positive_count+neutral_count)/len(tweets_dict))*100}% / 100%) ")
    elif negative_count > positive_count:
        custom_print(f"\tSorry, But '{keyword}' has not such good Reputation. ({(negative_count/len(tweets_dict))*100}% / 100%) ")
    else:
        custom_print(f"\t'{keyword}' has Decent Reputation.")

    custom_print()
    show_piechart([positive_count, negative_count, neutral_count])



def show_piechart(list_of_items):
    global exit_event

    ## For storing piechart label and values, from 'list_of_items'
    custom_dict = {}

    ## Checking If ctrl+c already pressed
    if exit_event.is_set(): sys.exit()

    ## Only appending those 'key&value' pair, which have some response value/tweet other than 0
    if list_of_items[0]: custom_dict["+ve opinion"] = [list_of_items[0], '#99ff99']
    if list_of_items[1]: custom_dict["-ve opinion"] = [list_of_items[1], '#ff4040']
    if list_of_items[2]: custom_dict["neutral opinion"] = [list_of_items[2], '#ffcc99']

    ## Checking If ctrl+c already pressed
    if exit_event.is_set(): sys.exit()

    mylabels = list(custom_dict.keys())
    myvalue = [value[0] for value in list(custom_dict.values())]
    myexplode = [0.0 for _ in range(len(custom_dict))]
    mycolors = [value[1] for value in list(custom_dict.values())]

    fig1, ax1 = plt.subplots()

    ax1.pie(myvalue, labels = mylabels, colors=mycolors, autopct='%1.1f%%', explode=myexplode, startangle=90, pctdistance=0.85)

    # draw center circle
    center_circle = plt.Circle((0,0), 0.72, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(center_circle)

    ax1.axis('equal')
    # plt.tight_layout()
    plt.title(f'Opinions From {sum(list_of_items)} Tweets')
    plt.show()



## Handling Ctrl+c signal
def signal_handler(signum, frame):
    global exit_event

    remove_progress_mark()
    error_display(desc = "User Interrupted!!, 'Ctrl+C' Pressed | Closing all threads ...", exit = False)
    exit_event.set()



## Locking while threads are running
def lock():
    global exit_event, show_progress

    while (active_count() != 1):
        
        ## Progress bar for threads
        if show_progress: custom_print(f"\tThere are {active_count() - 1} threads remaining...", end="\r")
        
        ## printing line, if progress bar is not active
        else: custom_print(f"\t[?] Waiting for finish of the Step.", end="\r")
    
    remove_progress_mark()

    ## If Ctrl+c already pressed
    if exit_event.is_set(): sys.exit()



## Helps to remove Progress marks, like -> "Tweets recvd 100/100", after progress bar complete
def remove_progress_mark():
    custom_print(" " * 50, end="\r")



## Showing errors with format
def error_display(desc, error = "", exit = True):
    custom_print(f"\n[-] {desc}\n", error = True)

    error = str(error)
    if not error.isspace() and error : custom_print(f"Full error desc -> {error}\n")

    if exit: sys.exit("Program exits ...")



########################################################################### FUNCTION AREA END


########################################################################### Variables & all

if __name__ == '__main__':

    clear_screen()


    ## Help menu
    description = """A Social media Scrapper tool for specifically Twitter to measure reponses of a particular keyword"""
    epilog = """
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
    """
    parser = AP(description=description, epilog=epilog, formatter_class=RawDescriptionHelpFormatter)


    ## Setting Up cmdline arguments
    parser.add_argument('-k', '--keyword', metavar='KEYWORD', type=str, help='Keyword to search.')
    parser.add_argument('-m', '--maxresult', metavar='MAX RESULTS', type=int, help='How many tweets, want to scan? (default - 10) ', default=10)
    parser.add_argument('-t', '--threads', metavar='THREADS', type=int, help='Maximum Threads to allow, (default - auto, " but less_than 500")')
    parser.add_argument('-p', '--progress', metavar='OPTIONAL', help='Show progress of tweets fetching. (default - "FALSE")', default=False, nargs="?", const=True)
    parser.add_argument('-u', '--unique', metavar='OPTIONAL', help='Need Unique Tweets? (It takes more time than normal) (default - "FALSE")', default=False, nargs="?", const=True)
    parser.add_argument('-o', '--output', metavar='CSV FILE PATH', type=str, help='File name to save results (.csv) (default - "scrapper_result.csv")', default="scrapper_result.csv")
    parser.add_argument('-y', '--yes', metavar='OPTIONAL', help='If the program prompt for "yes"/"no", Then It will set "Yes" to each question (asked from the program) (default - FALSE)', default=False, nargs="?", const=True)
    parser.add_argument('--silent', metavar="OPTIONAL", help='Not print anything, ONLY errors will display and saving will be done. (default - FALSE)', default=False, nargs="?", const=True)
    parser.add_argument('--install', metavar='REQUIRED ONCE', help='Before running it first time for scraping, Use this flag to download all necessary nltk libraries', default=False, nargs="?", const=True)

    arguments = parser.parse_args()

    ## Extracting values from cmdline arguments
    keyword = arguments.keyword
    max_results = arguments.maxresult
    output_filename = arguments.output
    show_progress = arguments.progress
    silent = arguments.silent
    max_threads = arguments.threads
    unique = arguments.unique
    all_yes = arguments.yes
    install_lib = arguments.install


    ## If "--install" argument is set
    if install_lib:
        
        ## Installing modules
        subprocess.check_call([sys.executable, "-m", "pip", "install", "demoji==1.1.0"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib==3.5.1"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk==3.7"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas==1.4.1"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tweepy==4.8.0"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "w3lib==1.22.0"])


        ## Importing nltk for downloading libraries
        import nltk

        ## Downloading, basic nltk libraries for work
        nltk.download('stopwords') # for stopwords
        nltk.download('vader_lexicon')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
        nltk.download('averaged_perceptron_tagger') # for nltk.pos_data()
        sys.exit("\n" + "All libraries downloaded !!")
    
    else:
        ## Trying If all modules are installed properly
        try:
            # For emoji work
            import demoji

            # For analysing sentiments, & helping in Tweet's Preprocessing
            import nltk
            from nltk.corpus import stopwords, wordnet
            from nltk.stem import WordNetLemmatizer
            from nltk.sentiment.vader import SentimentIntensityAnalyzer

            ## For support work
            from w3lib.html import replace_entities

            # For displaying the data after and saving to csv
            import pandas as pd
            import matplotlib.pyplot as plt

            # For gathering tweets
            import tweepy
        
        except Exception as error:
            error_display("One or more necessary Modules are absent, run 'python socialmedia_scraper.py --install' once", error = error)


    ## Setting Up "exit_event" & break_event for program :-
    exit_event = Event() # for Ctrl+c 
    break_event = Event() # for breaking starting_threads from for loop

    
    ## "delimiter" for "uniq" situation
    delimiter = "Æ"

    ## Twitter data tracking related variable
    Total_requests = 0
    Twitter_rate_limit_rq = 450 # 450 requests per 15 min.
    Twitter_rate_limit_min = 15 # 450 requests per 15 min.

    ## Limiting "max_results"
    if max_results >= 45000:
        error_display("Too much Value, Maximum value can be '45000'.", exit=False)
        ask_continue = input("Continue with 45000? (Y/n) ")
        if ask_continue.lower() != "y": sys.exit("\nExiting...")

    
    ## getting BEARER TOKEN
    try:

        ## for windows
        if os.name == 'nt':
            token = str(json.load(open("resources\\config.json", "r"))['Bearer Token'])
        
        ## for linux
        else: token = str(json.load(open("resources/config.json", "r"))['Bearer Token'])

        if not token and not token.isspace(): raise Exception
    
    except Exception as error:
        error_display(desc = "Invalid Bearer Token\n\nWhat Can I do?\n[ tip-1 ] Check Your Bearer Token once more.\n[ tip-2 ] Make Sure 'config.json' is in 'resources' dir.\n[ tip-3 ] Checkout Installaton Page of this tool - 'https://github.com/MAAYTHM/PySM'. ", error = error)

    try:
        
        ## checking if 'keyword' variable is blank or not
        if keyword != None:
            
            ## Modifying keyword value to lowercase
            keyword = str(keyword).lower()

            ## Checking if output file is set by user?
            if output_filename:

                ## Checking output_filename's extension and existence
                if output_filename[-4:] != '.csv': output_filename += '.csv'
                if os.path.exists(output_filename):

                    ## If "-y" argument is given?
                    if all_yes:
                        custom_print(f"File ('{output_filename}') already exists. Delete it and then Proceed.\nDelete - [Y/n] -> Y")
                        ask_delete = "y"
                    
                    else:
                        ask_delete = input(f"File ('{output_filename}') already exists. Delete it and then Proceed.\nDelete - [Y/n] -> ").lower()

                    custom_print()
                    if ask_delete == 'y' or not ask_delete:
                        os.remove(output_filename)
                        custom_print(f"File ({output_filename}) deleted successfully, Continuing Work ...")
                    else: error_display('File not deleted, & Exits ...')

                    ## Few seconds sleep
                    time.sleep(1)
                    clear_screen()
            
            
            ## Variables for "support_Purify" Class :-
            stopwords_set = set(stopwords.words("english"))
            pattern_stopwords = re.compile(r'\b(' + r'|'.join(stopwords_set) + r')\b\s*')
            word_lemmatizer = WordNetLemmatizer()
            pos_dict = {'A':wordnet.ADJ, 'S':wordnet.ADJ_SAT, 'R':wordnet.ADV, 'N':wordnet.NOUN, 'V':wordnet.VERB}
            pattern_punctuation = re.compile('[%s]' % re.escape(string.punctuation))

            try:
                ## for windows
                if os.name == 'nt':
                    words_dict = list(json.load(open("resources\\words_dict.json")).keys())
                
                ## for linux
                else: words_dict = list(json.load(open("resources/words_dict.json")).keys())
            
            except Exception as error:
                error_display(desc = f"File not found!!\n\nWhat Can I do?\n[ tip-1 ] Make Sure 'words_dict.json' is in 'resources' dir\n[ tip-2 ] Checkout Installaton Page of this tool - 'https://github.com/MAAYTHM/PySM'. ", error=error)

            WORDS = Counter(words_dict)


            ## Executing Main function
            main()

        elif not install_lib:
            error_display(desc = "the following arguments are required: -k/--keyword")

    except PermissionError as error:
        error_display(desc = "Improper Permission OR Rerun this Tool.", error = error)
    
    except RuntimeError or KeyboardInterrupt as error:
        error_display(desc = "User Interrupted!!, 'Ctrl+C' Pressed | Closing all threads ...", error = error)

    except Exception as error:
        error_display(desc = f'An error occured -> {error}')
