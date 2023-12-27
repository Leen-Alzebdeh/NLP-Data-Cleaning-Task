import re
import os
import random


def main():
    data_parent = "Data"
    clean_parent = "clean"
    transform_parent = "transformed"

    make_clean_trans_dirs(data_parent, clean_parent)

    global cmu_pronun_dict
    cmu_pronun_dict = make_dict()   # create dictionary
    make_clean_trans_dirs(clean_parent, transform_parent, 1)


def make_clean_trans_dirs(original_dir, new_dir, op=0):
    """
    Function creates clean and transformed directories
    original dir (string): name of the directory which we're copying files from.
    new_dir (string): name of directory we're creating
    op (int): 0 to create clean files, 1 to create transformed files 
    Return none
    """
    os.makedirs(new_dir, exist_ok=True)
    data_dir = os.listdir(original_dir)  # list all subdirectories in path

    for dir in data_dir:
        new_path = os.path.join(new_dir, dir)  # path in new directory
        original_path = os.path.join(original_dir, dir)  # path in parent
        try:
            # if we reaches files
            if '.' in dir:

                if dir.endswith(".cha"):
                    file_name = os.path.splitext(new_path)[0]+'.txt'
                    new_fp = open(file_name, 'w+', encoding='utf-8',
                                  errors='ignore')
                    # get text from cha file
                    og_text = open(original_path).read()
                    clean(og_text, new_fp)
                    new_fp.close()
                elif dir.endswith(".txt") & op:
                    file_name = new_path
                    new_fp = open(file_name, 'w',
                                  encoding='utf-8', errors='ignore')
                    clean_fp = open(original_path, 'r',
                                    encoding='utf-8', errors='ignore')
                    transform(clean_fp, new_fp)
                    new_fp.close()
                    clean_fp.close()
            else:
                # if not file, recusrisevely create subdirectory in new directory
                os.mkdir(new_path)
                make_clean_trans_dirs(original_path, new_path, op)
        except UnicodeDecodeError as e:
            pass
        except Exception as e:
            print(f"An error occurred: {e}")


def clean(og_text, clean_file):
    """
    Function cleans words in .cha file and writes them to clean file
    og_text (string): text from cha file to clean.
    new_file (file): opened file we're writing clean content to.
    Return none
    """

    # concatenat multi-lines (which start by a tab) cha text
    lines = (re.sub(r"\n\t", " ", og_text, flags=re.M | re.I)).split("\n")

    for line in lines:
        x = re.sub(r'^@.*', '', line.strip())  # remove headers
        x = re.sub(r'^%.*', '', x)  # remove lines that start with %
        x = re.sub(r'^\*\w*:\s', '', x)  # remove speaker tags
        # remove text including and between: NAK, [] and <>
        x = re.sub(r'[<\[].*[\]>]', '', x)
        # remove expression words like &=laughs
        x = re.sub(r'^&=.*\b', '', x)
        # remove @ and any character before and word chracters after
        x = re.sub(r'(\b\w)?@\w*\b', '', x)
        # replace hyphens and underscores with space
        x = re.sub(r'[_-]', " ", x)
        # remove all non-alphanumeric and space characters
        x = re.sub(r'[^a-zA-Z\s\']', '', x)
        x = re.sub(r'^ +', '', x)

        if len(x) != 0:
            x = re.sub(r'  +', " ", x)  # remove double spaces
            # only add line if it's not already in file
            clean_file.seek(0)
            if x not in clean_file.read():
                clean_file.write(x+'\n')


def transform(clean_file, trans_file):
    """
    Function transforms words in clean file and writes them to transformed file
    clean_file (string): clean file we're reading from.
    trans_file (file): opened file we're writing transformed content to.
    Return none
    """
    for line in clean_file:
        words = re.findall(r'\b[\w\']+\b', line)
        for word in words:
            word = word.lower()  # convert
            if word in cmu_pronun_dict:
                # Write the phonetic transcription with original capitalization
                trans_file.write(
                    ' '.join(random.choice(cmu_pronun_dict[word])) + ' ')  # pick randomly from the different pronunciations
            # if not in cmu dictionary
            else:
                phonetic_split_word = get_cmu_words(word)
                for split_word in phonetic_split_word.split():
                    if split_word in cmu_pronun_dict:
                        # Write the phonetic transcription with original capitalization
                        trans_file.write(' '.join(random.choice(
                            cmu_pronun_dict[split_word])) + ' ')
        trans_file.write('\n')


def get_cmu_words(word):
    """
    Function gets word not in cmu, iteratively and recusively splits it to get the largest tokens which are in cmu
    word (string): word not in cmu
    Return (string): word split into tokens present in cmu, divided by space
    """
    word_tokens = split_into_tokens(
        word)  # get all the possible tokens from word
    if word_tokens:
        cmu_words = []
        for word in word_tokens:
            # don't get words that are only a letter or other common sufficxes
            if len(word) == 1 or word == 'es' or word == 'ies':
                continue
            if word in cmu_pronun_dict:
                cmu_words.append(word)
        if len(cmu_words) == 0:
            return ''
        # get the largest word token that is in cmu
        max_word = max(cmu_words, key=len)
        # partition: get the suffix and prefix to the max word from word
        part_words = word.partition(max_word)
        return_word = ''
        for w in part_words:
            if w != max_word:  # recusrively find tokens in cmu from partitions
                return_word += get_cmu_words(w) + ' '
            else:  # attach max word
                return_word += max_word
        return return_word
    return ''


def split_into_tokens(word):
    """
    Function splits word into all possible tokens 
    word (string): word to be split into tokens
    Return (list): list of word tokens (strings)
    """
    # Find all word tokens within the input word
    matches = re.findall(r'(?=([a-zA-Z]+))', word)
    # Find all word tokens withtin reversed input word
    reverse_matches = re.findall(r'(?=([a-zA-Z]+))', word[::-1])[::-1]

    reverse_matches = [x[::-1] for x in reverse_matches]

    word_tokens = matches+reverse_matches[1:]

    return word_tokens


def make_dict():
    """
    Function makes dictionary from cmu file, with pronunciations in a list as a value for each key (word)
    word (string): word to be split into tokens
    Return (dictionary): cmu dictionary 
    """
    # replace all words with their phonetic pronunciations and write to new file
    # Load the CMU Pronouncing Dictionary
    cmu_pronun_dict = {}
    with open("dictionary.txt", 'r', errors="ignore") as dict_file:
        for line in dict_file:
            # Ignore lines that do not start with a letter
            if re.match(r'^[a-zA-Z]', line):
                parts = line.split()
                cmu_word = parts[0].lower()
                cmu_pronun = parts[1:]
                # if there are multiple pronunciations, add them to list in value
                if cmu_word.split("(")[0] in cmu_pronun_dict:
                    cmu_pronun_dict[cmu_word.split("(")[0]].append(cmu_pronun)
                else:
                    cmu_pronun_dict[cmu_word] = [cmu_pronun]
    return cmu_pronun_dict


main()
