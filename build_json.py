# -*- coding: utf-8 -*-
"""
Created on Fri Feb  3 08:44:50 2023

@author: xiuwenz2
"""

import json
import random
from itertools import islice
import numpy as np


file_group = ['lexicon', 'sentence', 'homograph']
file_usage = ['test', 'train', 'valid']
split_ratio = [[1, 98, 1], [2.5, 95, 2.5], [5, 90, 5]]


def random_dic(dicts):
    dict_key_ls = list(dicts.keys())
    random.seed(10)
    random.shuffle(dict_key_ls,)
    new_dic = {}
    for key in dict_key_ls:
        new_dic[key] = dicts.get(key)
    return new_dic


def split_dic(dicts, split_ratio):
    size = len(dicts)
    ratio = np.array(split_ratio) / sum(split_ratio)
    start = 0
    for i in range(len(split_ratio)):
        it = iter(dicts)
        end = round(size * sum(ratio[:i+1]))
        yield {k: dicts[k] for k in islice(it, start, end)}
        start = end



# SAMPLE

for group in file_group:
    for usage in file_usage:
        file_name = "sample/"+ group + "_" + usage +".json"
        with open(file_name, "r") as f:
        # with open("lexicon.json", "r") as f:
            json_data = json.load(f)
            print(json_data)



# DICT

f = open("cc_cedict.pinyin.dict",'r', encoding='UTF-8')
lines = f.readlines()
f.close()

cedict_dict = {}
for i, line in enumerate(lines):
        char = line.split()[0]
        phn = line.split()[1]
        cedict_dict["CEDICT-" + str(i)] = {'origin':'cc-cedict', 'char': char, 'phn': list(phn.strip(""))}
        
file_name = "lexicon.json"
with open(file_name, "w") as f:
    json.dump(cedict_dict,f)

file_name = "lexicon.json"
with open(file_name, "r") as f:
    json_data = json.load(f)

random_data = random_dic(json_data)
for i, dic in enumerate(split_dic(random_data,split_ratio[0])):
    new_file_name = "json/lexicon_" + file_usage[i] + ".json"
    with open(new_file_name, "w") as f:
        json.dump(dic,f)



# SENTENCE

sen_dict = {}
for cat in ["test", "train"]:
    f = open("aishell/" + cat + "-content.txt", 'r', encoding='UTF-8')
    lines = f.readlines()
    f.close()
    for i, line in enumerate(lines):
        sen_id = line.split()[0][:-4]
        mix_char = line.split()[1::2]
        char = " ".join(mix_char)
        sen_dict[sen_id] = {'origin': 'aishell-3', 'char': char}

f = open("aishell/pinyin-content.txt", 'r', encoding='UTF-8')
lines = f.readlines()
f.close()
for i, line in enumerate(lines):
    sen_id = line.split()[0]
    # if sen_id in sen_dict.keys():
    mix_phn = line.split()[1:]
    phn = [" " if i == '|' else i for i in mix_phn]
    sen_dict[sen_id]['phn'] = phn

print(len(sen_dict))

file_name = "sentence.json"
with open(file_name, "w") as f:
    json.dump(sen_dict,f)

file_name = "sentence.json"
with open(file_name, "r") as f:
    json_data = json.load(f)

random_data = random_dic(json_data)
for i, dic in enumerate(split_dic(random_data,split_ratio[1])):
    new_file_name = "json/sentence_" + file_usage[i] + ".json"
    with open(new_file_name, "w") as f:
        json.dump(dic,f)


# HOMOGRAPH

cedict_homo = {}
file_name = "lexicon.json"
with open(file_name, "r") as f:
    json_data = json.load(f)

for key in json_data.keys():
    char = json_data[key]['char']
    if char not in cedict_homo:
        cedict_homo[char] = 1
    else:
        cedict_homo[char] += 1

# for key in sen_dict.keys():
homo_dict = {}
homo_id = 0
for key in sen_dict.keys():
    total_index = 0
    last_index = 0
    sentence = sen_dict[key]['char']
    phn_sentence = sen_dict[key]['phn']
    char_list = sentence.split(' ')
    for char in char_list:
        total_index += len(char) - 1
        try:
            if cedict_homo[char] != 1:
                char_index = sentence.find(char, last_index, len(sentence))
                phn_index = [i for i in range(len(phn_sentence)) if phn_sentence[i] == ' ']
                phn_index.append(len(phn_sentence))
                if char_index == 0:
                    phn_start = 0
                    phn_end = phn_index[0]
                else:
                    phn_start = phn_index[int((char_index-total_index)/2)-1] + 1
                    phn_end = phn_index[int((char_index-total_index)/2)]
                homo_dict["AIS-" + str(homo_id)] = {'origin': 'aishell-3',
                                                    'char': sentence,
                                                    'phn': phn_sentence,
                                                    'homograph': char,
                                                    'homograph_char_start': char_index,
                                                    'homograph_char_end': char_index + len(char),
                                                    'homograph_phn_start': phn_start,
                                                    'homograph_phn_end': phn_end}
                homo_id += 1
                last_index = char_index + len(char)
        except KeyError:
            char_index = sentence.find(char, last_index, len(sentence))
            last_index = char_index + len(char)
    
file_name = "homograph.json"
with open(file_name, "w") as f:
    json.dump(homo_dict,f)

file_name = "homograph.json"
with open(file_name, "r") as f:
    json_data = json.load(f)

random_data = random_dic(json_data)

for i, dic in enumerate(split_dic(random_data, [10259,484409-10259])):
    if i == 0:
        split_data = dic
        
for i, dic in enumerate(split_dic(split_data, split_ratio[2])):
    new_file_name = "json/homograph_" + file_usage[i] + ".json"
    with open(new_file_name, "w") as f:
        json.dump(dic,f)



# RESULT
for group in file_group:
    for usage in file_usage:
        file_name = "json/"+ group + "_" + usage +".json"
        with open(file_name, "r") as f:
            json_data = json.load(f)
            if group == file_group[1]:
                print(json_data.values())