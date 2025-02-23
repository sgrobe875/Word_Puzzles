# Created June 2023
# Last updated February 2024


# DIRECTIONS:
# Click the "Run" button in the top right corner - it looks like a small arrow, like a "play" button
# On the bottom of the screen, in the window labeled "Terminal," wait until you see the prompt "Type any word"
# Click to the right of the prompt, type a word, and hit the return/enter key. Be sure not to add any spaces or punctuation
# To run a search on another word, just repeat these steps!


# As you're playing with this, please let me know about any changes I can make, including words/phrases you want to see added,
# words/phrases you want removed, or any changes that would be helpful in how the output of the word lists are presented.


# SUMMARY:
# This script takes in a word as user input and returns a list of words (one-grams) and two-word phrases (two-grams)
# that either start or end with the user's word, provided that the remainder of the one- or two-gram is also a valid word.
# Words are validated using both online and locally stored data sources.


# Baseline one-grams data set courtesy of Manas Sharma: https://www.bragitoff.com/2016/03/english-dictionary-in-csv-format/
# Two-grams and additional one-grams from the free dictionary: https://www.thefreedictionary.com/s/ and https://www.thefreedictionary.com/e/
# Word frequencies from Kaggle/Google Books Ngram Viewer: https://www.kaggle.com/datasets/wheelercode/english-word-frequency-list?resource=download


# import necessary packages
import pandas as pd
import requests
import datetime
import re
import os
import json
from collections import Counter


# clear the contents of the terminal at the start of each run, to help keep things easy to read
os.system('clear') 


# set the working directory to be wherever this file is stored
# as long as necessary data files are stored in the same location as this file, we will never encounter a FileNotFound error 
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)




# creates the file one_grams.csv from a number of word lists found online
# this function should only ever need to be run once, but leaving it here for reference
def clean_and_build_file():
    # print console update that process is starting
    e = datetime.datetime.now()
    print ("Beginning at %s:%s:%s" % (e.hour, e.minute, e.second))
    
    # empty list to hold all words
    words = []
    
    # all 26 letters; used to identify the individual word files
    letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M',
               'N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    
    # remove these words as we find them
    fake_words = ['ing','bede','ery','lin','lar','ped']
    
    # loop through every letter
    for letter in letters:
        # open the letter's corresponding file of words
        filename = 'word_lists/'+letter+'word.csv'
        curr_df = pd.read_csv(filename, header=None, engine='python', error_bad_lines=False, encoding="ISO-8859-1")
        
        # loop thorugh each word in the
        for i in range(len(curr_df)):
            curr_word = curr_df.iloc[i,0]
            
            # strip away any whitespace, newlines, etc.
            curr_word = curr_word.strip()
            
            # set to lowercase if not already
            if not curr_word.islower():
                curr_word = curr_word.lower()
        
            # skip if meets any of the following criteria
            if ((not curr_word.isalpha() and ('-' not in curr_word or '_' not in curr_word)) or 
                "aa" in curr_word or "abc" in curr_word or curr_word[-1] == '-' or 
                curr_word[0] == '-' or len(curr_word) == 1 or curr_word in fake_words):
                pass
            
            else:
                if '_' in curr_word:
                    sp = curr_word.split('_')
                    words.append(sp[0])
                else:
                    words.append(curr_word)

    
    # cast to a Counter; this will make each unique word a key
    no_dups = dict(Counter(words))
    
    # get all unique words by grabbing the Counter keys
    words = no_dups.keys()
    
    # print update that we're finished
    e = datetime.datetime.now()
    print ("Finished at %s:%s:%s" % (e.hour, e.minute, e.second))
    
    # set to pandas dataframe so we can export
    word_df = pd.DataFrame(words)
    
    # save to csv
    word_df.to_csv('one_grams.csv', index=False)
        
    
    
# Similar to the function above, this function is really only needed the first time, or any time you wish to 
# reset or overwrite the list of word frequencies; leaving this function here for reference
def build_and_export_frequencies():
    # read in the list of words and their frequencies
    freq_df = pd.read_csv('ngram_freq.csv')
    
    # now limit to just reasonably popular words (> 1000 uses)
    freq_df = freq_df[freq_df['count'] > 1000]
    
    # now create a dictionary in the format {word:frequency}
    word_freqs = {}
    
    # begin by looping through each row of the dataframe
    for r in range(len(freq_df)):
        # add to dictionary using the word as the key and the count as the value
        word_freqs[freq_df.iloc[r]['word']] = int(freq_df.iloc[r]['count'])
        
    # save the dictionary as a json file so we don't have to build the dictionary every time
    with open("word_freqs.json", "w") as outfile: 
        json.dump(word_freqs, outfile)
    
    
    
    
    
    

#### MAIN #################################################################################################################
    

#### Call above functions, if necessary ####
    
# only call this function to reset the data set of one grams! Otherwise, leave it commented out
# clean_and_build_file()

# only call this function to reset the data set of word frequencies; otherwise, leave it commented out
# build_and_export_frequencies()






#### Read in and manipulate data files ####

# read in data set of one-grams
data = pd.read_csv('one_grams.csv')

# convert to list of words
words = list(data.iloc[:,0])

# ensure everything was read in as a string
words = [str(word) for word in words]


# read in the json to get a dictionary of word frequencies; we'll use this later
word_freqs = json.load(open('word_freqs.json'))






#### User input #####


# get input from the user for the word of interest
user_word = input("\nType any word: ")

# set to lowercase
user_word = user_word.lower()





 
#### Manual tweaks to the word list ####


# probably overkill since these changes will always be saved to a file at the end of each run, but to
# be safe, we'll just make these checks every time we run the script

# words that we noticed are not in the word list that we would like added
add_words = ['gam']

# words that should never be added to the word list, and should be removed if they are already present
blacklisted_words = []


# loop through the words to add; add to the word list if not already present
for add_word in add_words:
    if add_word not in words:
        words.append(add_word)
        
        
# loop through blacklisted words; if present in the word list, remove them
for blacklisted_word in blacklisted_words:
    if blacklisted_word in words:
        words.remove(blacklisted_word)


# now we can move on to getting results!






#### Web scraping! ####



## Get starting words ##

# First, scrape for one-grams that aren't in our existing data set plus two-grams that START with the word

# URL - '/s/' indicates "starting" with the word; append the user's word to get the complete URL
URL = 'https://www.thefreedictionary.com/s/' + user_word

# get all HTML from the web page
page = requests.get(URL)
text = page.text

# flag for whether the user entered a valid word; assume valid until proven otherwise
valid_search = True

# if a space is present, set search to invalid
if ' ' in user_word:
    valid_search = False

try:
    # "class=suggestions" within the ul html elements is indicative solely of the dictionary results
    # find the first instance of this (aka the beginning of the results)
    start_index = [m.start() for m in re.finditer('class=suggestions', text)][0]
    
# if we get an IndexError here, it means the word was not found on the free dictionary (i.e., it is not valid)
# change the valid_search flag to False
except IndexError:
    valid_search = False
    
    
# if the word was determined to be invalid above, stop here; if it's valid, proceed with the rest of the script
if valid_search:
    # results are returned in several consecutive ul elements with the suggestions tag; find the last ul element of this type
    last = [m.start() for m in re.finditer('class=suggestions', text)][-1]
    
    # next, find all locations with the ul closing tag (not all of these will correspond to a suggestion ul)
    ends = [m.start() for m in re.finditer('</ul>', text)]
    
    # find the location of the first ul closing tag that is after the last suggestion tag
    # this will indicate the ending location of the suggestions
    # do this by looping through locations of all ul closing tags
    for i in ends:
        # find the first one after the last suggestions tag and then break out of the loop
        if i > last:
            end_index = i
            break
    
    # within this subset of the text that we just found above, extract everything that falls between
    # the end of one tag and a closign anchor tag
    # this will give us a list of all of the suggestions from the webpage
    results = re.findall(r'">.*?</a>', text[start_index:end_index])
    
    # remove first two characters adn last four characters from each result (the html pieces that we used to find them)
    # also set all characters to lowercase
    cleaned_results = [result[2:-4].lower() for result in results]
    
    # initialize an empty list to hold the two-grams starting with the user's word
    two_grams_start = []
    
    # loop through all cleaned results/suggestions
    for result in cleaned_results:
        # filter out any of the irrelevant results that contain certain punctuation
        if '-' not in result and '(' not in result and ',' not in result:
            # split on spaces to get a list of words from our result
            split_words = result.split(' ')
            
            # if one-gram, check if in the one-grams list already
            if len(split_words) == 1:
            # if not, add it; if it's already in the list, just move on
                if result not in words:
                    words.append(result)
    
            # if two-gram, check to make sure it meets our criteria
            elif len(split_words) == 2:
                # Check the two criteria: first word must be exactly equal to the user word
                # AND the second word must be in our one-grams data set
                if split_words[0] == user_word and split_words[1] in words:
                    # if it meets both criteria, add to the list; otherwise, just move on
                    two_grams_start.append(result)
            
            
            # anything else, just skip
            
        
        
    ## Get ending words ##
        
    # repeat the above, but now for two-grams that END with the word
    
    
    # use the '/e/' link to get words ending with our word of interest
    URL = 'https://www.thefreedictionary.com/e/' + user_word
    
    # otherwise, workflow is identical to above
    
    # get the HTML from the page
    page = requests.get(URL)
    text = page.text
    
    
    # find beginning and end of the suggestions in same manner as above
    start_index = [m.start() for m in re.finditer('class=suggestions', text)][0]
    last = [m.start() for m in re.finditer('class=suggestions', text)][-1]
    
    ends = [m.start() for m in re.finditer('</ul>', text)]
    
    for i in ends:
        if i > last:
            end_index = i
            break
    
    # use the indicies found above to collect all suggestions, clean them, and store in a list
    results = re.findall(r'">.*?</a>', text[start_index:end_index])
    
    cleaned_results = [result[2:-4].lower() for result in results]
    
    
    # empty list to store our relevant two-grams
    two_grams_end = []
    
    
    
    # loop through all cleaned results
    for result in cleaned_results:
        # ignore those containing punctuation
        if '-' not in result and '(' not in result and ',' not in result:
            split_words = result.split(' ')
            # if one-gram, check if in the one-grams list already
            if len(split_words) == 1:
            # if not, add it; if it's already in the list, just move on
                if result not in words:
                    words.append(result)
    
            # if two-gram, check to make sure it meets our criteria
            elif len(split_words) == 2:
                # Check the two criteria: second word must be exactly equal to the user word
                # AND the first word must be in our one-grams data set
                if split_words[1] == user_word and split_words[0] in words:
                    # if it meets both criteria, add to the list; otherwise, just move on
                    two_grams_end.append(result)
    
    
            # if > two-gram, skip
            
            
            
            
    
    
    #### Combine and organize results for the user ####
    
    
    ## Words that START with the user's word ##
    
    # list of all one-grams that start with user_word AND the remainder of the one_gram is also in the list
    # of acceptable one-grams
    starting = [word for word in words if (len(word) > len(user_word) and user_word == word[:len(user_word)]
                                            and word[len(user_word):] in words)]
    
    # append the list of two-grams starting with our word to this list
    starting = starting + two_grams_start
    
    
    # clear starting list of any of our blacklisted words
    for blacklisted_word in blacklisted_words:
        if blacklisted_word in starting:
            starting.remove(blacklisted_word)
    
    
    # build a dataframe of starting words and their frequencies; we'll use this to sort them
    starting_counts = []
    
    # loop through each word in our starting list
    for word in starting:
        # start by checking if it's a two-gram
        if ' ' in word:
            # if it is, grab the frequency of the non-user word (in this case, the second word)
            try:
                word_split = word.split(' ')
                starting_counts.append(word_freqs[word_split[1]])
            # if the frequency is not available, just append a zero
            except KeyError:
                starting_counts.append(0)
                
        # if no space, then it must be a one-gram
        else:
            # try to get the frequency of the word directly
            try:
                starting_counts.append(word_freqs[word])
            # if we don't have a frequency available, just append a zero
            except KeyError:
                starting_counts.append(0)
    
    # create a dataframe from the two lists
    starting_df = pd.DataFrame({'word':starting, 'counts':starting_counts})
    
    # sort the dataframe by counts (descending)
    starting_df_counts = starting_df.sort_values('counts', ascending = False)
    
    ## another version, sorted alphabetically

    # start by creating another column for the dataframe for sorting
    words_for_sorting = []
    
    # loop through each word in the results
    for word in starting_df['word']:
        # check if it has a space (aka, if it's a two-gram)
        if ' ' in word:
            # if it is, split and rebuild the word without the space
            word_split = word.split(' ')
            fixed_word = word_split[0] + word_split[1]
            
            # add to the list
            words_for_sorting.append(fixed_word)
            
        else:
            # if it doesn't have a space, add it to the list as is
            words_for_sorting.append(word)
            
    # add the list to the dataframe as a new column
    starting_df['word for sorting'] = words_for_sorting
    
    # sort by the new column
    starting_df_alpha = starting_df.sort_values('word for sorting', ascending = True)
    
    # overwrite the list of starting words to be this one that we just sorted
    starting = list(starting_df_alpha['word'])
    
    
    
    ## Words that END with the user's word
    
    # same workflow as above for one-grams ending with our word
    ending = [word for word in words if (len(word) > len(user_word) and user_word == word[-len(user_word):]
                                          and word[:-len(user_word)] in words)]
    
    # append the list of two-grams ending with our word
    ending = ending + two_grams_end
    
    
    # clear starting list of any of our blacklisted words
    for blacklisted_word in blacklisted_words:
        if blacklisted_word in ending:
            ending.remove(blacklisted_word)
    
    
    # build a dataframe of ending words and their frequencies; we'll use this to sort them
    ending_counts = []
    
    # loop through each word in our ending list
    for word in ending:
        # check if two-gram
        if ' ' in word:
            # if it is, grab the frequency of the non-user word (in this case, the first word)
            try: 
                word_split = word.split(' ')
                ending_counts.append(word_freqs[word_split[0]])
            # if the frequency is not available, just append a zero
            except KeyError:
                ending_counts.append(0)
        
        # otherwise must be a one-gram
        else:
            # try to pull the word's frequency from the dictionary and add to our list of counts
            try:
                ending_counts.append(word_freqs[word])
            # if we don't have a frequency available, just append a zero
            except KeyError:
                ending_counts.append(0)
    
    # create a dataframe from the two lists
    ending_df = pd.DataFrame({'word':ending, 'counts':ending_counts})
    
    # sort the dataframe by counts (descending)
    ending_df_counts = ending_df.sort_values('counts', ascending = False)
    
    ## another version, sorted alphabetically

    # start by creating another column for the dataframe for sorting
    words_for_sorting = []
    
    # loop through each word in the results
    for word in ending_df['word']:
        # check if it has a space (aka, if it's a two-gram)
        if ' ' in word:
            # if it is, split and rebuild the word without the space
            word_split = word.split(' ')
            fixed_word = word_split[0] + word_split[1]
            
            # add to the list
            words_for_sorting.append(fixed_word)
            
        else:
            # if it doesn't have a space, add it to the list as is
            words_for_sorting.append(word)
            
    # add the list to the dataframe as a new column
    ending_df['word for sorting'] = words_for_sorting
    
    # sort by the new column
    ending_df_alpha = ending_df.sort_values('word for sorting', ascending = True)
    
    # overwrite the list of ending words to be this one that we just sorted
    ending = list(ending_df_alpha['word'])
    
    
    
    
    
    
    #### Print the finalized results to the console ####
    
    # start with displaying the user's word
    print()
    print()
    print('Printing results ALPHABETICALLY:')
    print()
    print('Words with "' + user_word + '"')
    print()
    
    # table header
    print('At the end (%-34s              At the beginning (%-16s' % (str(len(ending)) + ' results)', str(len(starting)) + ' results)'))
    print('---------------------------------------------------------------------------------------------------')
    
    # show lists side by side, which means the number of rows in our table = length of the longer list (starting vs. ending)
    for i in range(max(len(starting), len(ending))):
        try:
            # start with fetching the beginning piece of words ENDING with our word
            w1 = ending[i][:-len(user_word)]
            # then fetch the entire word all together
            w2 = ending[i]
        # if we get an error, it means this list was the shorter of the two; just use blank spaces
        except IndexError:
            w1 = ''
            w2 = ''
            
        try:
            # start with fetching the entire word
            w3 = starting[i]
            # next fetch the end of the word that is left after removing user_word at the beginning
            w4 = starting[i][len(user_word):]
            # check for the presence of a space
            if ' ' in starting[i]:
                # if we find one, it means this is a two-word phrase, so remove the space from the stem
                w4 = starting[i][len(user_word)+1:]
            
        # if we get an error, it means this list was the shorter of the two; just use blank spaces
        except IndexError:
            w3 = ''
            w4 = ''
        
        
        # when we're out of words in the first column, but still have words to print in the second
        # column; avoids printing the arrow between the blank spaces
        if len(w1) == 0 and len(w2) == 0:
            print('%-14s       %-38s %-20s -->   %-15s' % (w1, w2, w3, w4))
        
        # same as above, but for when we have something to print in the first column but not the second
        elif len(w3) == 0 and len(w4) == 0:
            print('%-14s -->   %-38s'  % (w1, w2))
        
        # this is essentially the default: when we have an entry to print in both columns
        else:
            print('%-14s -->   %-38s %-20s -->   %-15s' % (w1, w2, w3, w4))
    
    
    
    
    
    
    #### Last check and save final results ####
    
    # one last check to clean out any blacklisted words before we export to a file
    for blacklisted_word in blacklisted_words:
        if blacklisted_word in words:
            words.remove(blacklisted_word)
    
    
    
    #### at the end, rewrite the data files to save any changes that were made ####
    words_df = pd.DataFrame(words)
    words_df.to_csv('one_grams.csv', index=False)



# only reach this point if the user's word was invalid; print message to the console
else:
    print('\nNo matches found! Double check that you\'ve entered a valid word and try again.')
    print('Remember not to include any punctuation or spaces!')


# to help keep the console clean and easy to read, print a few newlines at the end
print('\n\n')




