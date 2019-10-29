from zeep.client import Client
import random
from .utils import is_fa,remove_puncs,STOP_WORDS,preprocess


class Augment:
    def __init__(self, farsnet_userkey):
        self.userkey = farsnet_userkey

    def get_synonyms(self, word):
        all_syns = []

        syn_url = 'http://farsnet.nlp.sbu.ac.ir/WebAPI/services/SynsetService?WSDL'
        sen_url = 'http://farsnet.nlp.sbu.ac.ir/WebAPI/services/SenseService?WSDL'

        client = Client(syn_url)

        syns = client.service.getSynsetsByWord(
            searchStyle='EXACT', searchKeyword=word, userKey=self.userkey)

        client = Client(sen_url)
        for val in syns:
            if val['id'] != None:
                senses = client.service.getSensesBySynset(
                    synsetId=val['id'], userKey=self.userkey)
                for s in senses:
                    all_syns.append(s['word']['defaultValue'])

        return list(set(all_syns))

    def synonym_replacement(self, words, n):
        new_words = words.copy()
        random_word_list = list(set([word for word in words if is_fa(word) and word not in STOP_WORDS]))
        random.shuffle(random_word_list)
        num_replaced = 0
        for random_word in random_word_list:
            synonyms = self.get_synonyms(random_word)
            if len(synonyms) >= 1:
                synonym = random.choice(list(synonyms))
                new_words = [synonym if word ==
                             random_word else word for word in new_words]
                
                num_replaced += 1
            if num_replaced >= n:  # only replace up to n words
                break

        sentence = ' '.join(new_words)
        new_words = sentence.split(' ')

        return new_words
    
    def random_deletion(self,words, p):
        if len(words) == 1:
            return words

        #randomly delete words with probability p
        new_words = []
        for word in words:
            r = random.uniform(0, 1)
            if r > p:
                new_words.append(word)

        #if you end up deleting all words, just return a random word
        if len(new_words) == 0:
            rand_int = random.randint(0, len(words)-1)
            return [words[rand_int]]

        return new_words

    def random_swap(self,words, n):
        new_words = words.copy()
        for _ in range(n):
            new_words = self.swap_word(new_words)
        return new_words

    def swap_word(self,new_words):
        random_idx_1 = random.randint(0, len(new_words)-1)
        random_idx_2 = random_idx_1
        counter = 0
        while random_idx_2 == random_idx_1:
            random_idx_2 = random.randint(0, len(new_words)-1)
            counter += 1
            if counter > 3:
                return new_words
        new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1] 
        return new_words

    def random_insertion(self,words, n):
        new_words = words.copy()
        for _ in range(n):
            self.add_word(new_words)
        return new_words

    def add_word(self,new_words):
        synonyms = []
        counter = 0
        while len(synonyms) < 1:
            random_word = new_words[random.randint(0, len(new_words)-1)]
            synonyms = self.get_synonyms(random_word)
            counter += 1
            if counter >= 10:
                return
        random_synonym = synonyms[0]
        random_idx = random.randint(0, len(new_words)-1)
        new_words.insert(random_idx, random_synonym)
        
    def augment_sent(self,sentence:str,alpha_sr=0.1, alpha_ri=0.1, alpha_rs=0.1, p_rd=0.1, num_aug=9)->list:
        sentence = remove_puncs(sentence)
        words = sentence.split(' ')
        num_words = len(words)
        
        augmented_sentences = []
        num_new_per_technique = int(num_aug/4)+1
        n_sr = max(1, int(alpha_sr*num_words))
        n_ri = max(1, int(alpha_ri*num_words))
        n_rs = max(1, int(alpha_rs*num_words))

        #sr
        for _ in range(num_new_per_technique):
            a_words = self.synonym_replacement(words, n_sr)
            augmented_sentences.append(' '.join(a_words))

        #ri
        for _ in range(num_new_per_technique):
            a_words = self.random_insertion(words, n_ri)
            augmented_sentences.append(' '.join(a_words))

        #rs
        for _ in range(num_new_per_technique):
            a_words = self.random_swap(words, n_rs)
            augmented_sentences.append(' '.join(a_words))

        #rd
        for _ in range(num_new_per_technique):
            a_words = self.random_deletion(words, p_rd)
            augmented_sentences.append(' '.join(a_words))

        augmented_sentences = [preprocess(sentence) for sentence in augmented_sentences]
        random.shuffle(augmented_sentences)

        #trim so that we have the desired number of augmented sentences
        if num_aug >= 1:
            augmented_sentences = augmented_sentences[:num_aug]
        else:
            keep_prob = num_aug / len(augmented_sentences)
            augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

        #append the original sentence
        augmented_sentences.append(sentence)

        return augmented_sentences
