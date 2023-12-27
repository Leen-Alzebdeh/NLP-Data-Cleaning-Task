Here we provide justifications that detail the data cleaning and transformation choices we made.

Our downstream task: creating a language model that represents the likelihood of different sound sequences in English. Note that you will be using the data you clean in a later assignment.

# Details and Justifications of Our Choices

## Data Cleaning
| Regular Expression | Our Choice | Justification | 
| ---------- | ------------- | ----------| 
|  <pre>lines = (re.sub(r"\n\t", " ", og_text,<br>  flags=re.M \| re.I)).split("\n")</pre> | Concatenate multi-lines (which start with a tab) in the cha text files. | We decided to join the multi-lines together to allow proper cleaning line-by-line. | 
| <pre>x = re.sub(r'^@.\*', '', line.strip())</pre> | Removes headers that start with @, and replaces the entire line with nothing. | Removing headers is needed to ensure that data is not polluted with text that is not a part of speech. |
| <pre>x = re.sub(r'^%.\*', '', x)</pre> | Removes lines that start with %, and replaces the entire line with nothing. | Removing lines starting with a “%” is needed because we do not need context lines (non-speech data) in speech data. |
| <pre>x = re.sub(r'^\\*\w\*:\s', '', x)</pre> | Removes speaker tags. | We do not need speaker tags, as it is not speech data. Including speaker tags would pollute our speech data. |
| <pre>x = re.sub(r'[<\[].\*[\]>]', '', x)</pre> | Remove text including, and between: NAK, [ ], and <> | Text within these characters is for context or non-speech notations, which is not needed for our data. |
| <pre>x = re.sub(r'^&=.\*\b', '', x)</pre> | Remove expression words like “&=laughs” | These are context/non-speech notations, which are not needed for our data. |
| <pre>x = re.sub(r'(\b\w)?@\w\*\b', '', x)</pre> | Remove @ and any character to its left, and any word to its right | These are pieces of extra information/ form markers which are not part of speech. |
| <pre>x = re.sub(r'[_-]', " ", x)</pre> | Replace hyphens and underscores with space. | These are special characters that are not needed in speech data. In the case of words that have hyphens between them (e.g. non-confrontational), the word retains its phenome transformation without the hyphen or underscore. |
| <pre>x = re.sub(r'[^a-zA-Z\s\']', '', x)</pre> | Remove all non-alphabetic, apostrophe and space characters. | Space, apostrophes and alphabetic characters are all that is required to get the words’ phenomes during transformation. |
| <pre>x = re.sub(r'^ +', '', x)</pre> | Remove double spaces | To retain a normal writing structure. |


## Data Transformation
| Regular Expression | Our Choice | Justification | 
| ---------- | ------------- | ----------| 
| <pre>for line in clean_file:<br>  words =<br>    re.findall(r'\b[\w\']+\b', line)</pre> | For each line in the clean text files, find all the words and apostrophes. | We need to find all words, as well as apostrophes to save all the words from the data cleaning to use in data transformations. The apostrophes are needed for words like contractions (e.g. can’t, won’t, doesn’t). |
| <pre>matches =<br>  re.findall(r'(?=([a-zA-Z]+))', word)</pre> | Find all word tokens within the input word. | We try to find all possible matches from left to right as the first step in finding which match would be the largest matching match in the CMU dictionary. |
| <pre>reverse_matches =<br>  re.findall(r'(?=([a-zA-Z]+))',<br>    word[::-1])[::-1]</pre> | Find all word tokens within the reversed input word. | As we found all possible matches from left to right, we then wanted to find all possible matches right to left. This is because an input word may be “iydesk”, where “desk” can only be isolated as a word when looking right to left. |
| <pre>if re.match(r'^[a-zA-Z]', line):</pre> | Find lines that don’t start with a letter (and ignore those lines → if statement) | Finding lines that only start with a letter is essential to filter out all dictionary entries of words from the non-word related dictionary entries. |


## Impact of Our Choices
| Choices We Made | What We Gain | What We Compromise |
| ---------------- | ---------- | -------------|
| Include lexical markers | We gain extra data about phenomes in terms of variation of phenome stresses. This can be beneficial when further analyzing variability in phenome frequency. | This can lead to increased model complexity. |
| Include non-word utterances | Because non-word utterances are still compromised of phenomes, we gain a larger amount of reliable data to base future models upon.<br>Another factor is that “filler” non-word utterances can be more common within speech in certain cultures, and can actually be intentional. An example of this would be “uh” or “um” where these utterances can be conceived as words that allow the speaker to communicate that they are thinking about something before speaking. The inclusion of “um” in the CMU dictionary is reflective of the importance of including these utterances, as they do hold meaning. | The inclusion of non-word utterances can introduce noise into the dataset, necessitating more refined algorithms to discern between meaningful content and filler, “meaningless” sounds. |
| Remove unintelligible speech such as xxx or yyy | Unintelligible speech can produce inaccurate phenomes as other words were supposed to be said. Thus we prevent skewing results. | By removing these elements, the model may lose insight into the natural flow of speech, potentially affecting its performance in real-world applications. |
| Remove repeating lines in a file. | Repeating lines, which are especially common in children, can unnecessarily skew the likelihood representations, not due to the true high usage of those sequences in words in different contexts/ sentences, but only due to repetitio, comparable to spam data. This approach balances representativeness more. | In everyday speech, repetition is common and removing repeating lines may result in the model missing out on learning these inherent patterns of the language, which could be important for predicting realistic and coherent text.<br><br>In addition, some repetitions might reflect genuinely common or popular phrases, expressions, or sound sequences. Removing them might underemphasize their significance and prevalence in the language, potentially affecting the model's ability to prioritize and recognize commonly used sequences. However, since repeating phrases per single file are removed, this impact is likely not very big.<br><br>Repetition can be an element in the rhythm and flow of natural and everyday speech. Removing it might lead to a model that does not fully capture rhythmic patterns. |
| How we deal with words not in the CMU: iteratively and recursively find tokens in the word which are in the CMU, but discard one-letter tokens, “es” and “ies.”<br><br>More detail: we find all possible tokens in the word (and the reversed word), find what is the biggest token present in the CMU (max word), and partition the original word around the max word, we then find if the partitions are in the CMU, if they are not, we repeat this process recursively. The result returned is all tokens found in CMU from the word. | Rather than toss the word, we gain some or all of the word’s phonetics, resulting in no, or less loss of data. Example: gumball breaks down into the tokens gum ball.<br><br>Another benefit of including words not in the CMU is that these words may be part of commonly spoken slang in different communities.<br><br>Example: “lowkey” would be broken down to low key. | We face cases where the partitioned tokens can be common suffixes which are pronounced differently depending on the original word. Example: gaslighter breaks down to gaslight er. A similar problem can occur for prefixes of a word in partitions. |
| Use “proper” pronunciations of words.<br><br>Example: Use pull them out  instead of pull em out. | 1. Using proper pronunciations enhances consistency and standardization across the dataset, creating a potentially more robust model.<br><br>2. Proper pronunciations contribute to clearer and more distinct phonetic representations. This assists the model in accurately recognizing and representing the various sound sequences in English, which is pivotal for the downstream task.<br><br>3. In addition, training the model on standardized forms of words can potentially enhance its ability to generalize across various contexts and applications, thereby increasing its utility and reliability. | By opting for proper pronunciations, the dataset might lose the diversity of informal and colloquial speech patterns. This could limit the model’s ability to accurately represent and understand everyday, conversational English.<br><br>The model as a result could be biased towards standardized English at the expense of slang, dialects and informal English. |








