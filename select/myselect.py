import os
import torch
from transformers import AutoTokenizer
import numpy as np
import json
import random
import copy

device = f'cuda:{0}'

class K_means():
    def __init__(self, data, k):
        self.data = data
        self.k = k

    def distance(self, p1, p2):
        return torch.sum((p1-p2)**2).sqrt()

    def generate_center(self):
        n = self.data.size(0)
        rand_id = random.sample(range(n), self.k)
        center = []
        for id in rand_id:
            center.append(self.data[id])
        return center

    def converge(self, old_center, new_center):
        flag = True
        for i in range(self.k):
            flag = torch.equal(old_center[i], new_center[i])
            if flag == False:
                break
        return flag

    def forward(self):
        center = self.generate_center()
        n = self.data.size(0)
        labels = torch.zeros(n).long()
        flag = False
        while not flag:
            old_center = copy.deepcopy(center)

            for i in range(n):
                cur = self.data[i]
                min_dis = 10*9
                for j in range(self.k):
                    dis = self.distance(cur, center[j])
                    if dis < min_dis:
                        min_dis = dis
                        labels[i] = j

            for j in range(self.k):
                center[j] = torch.mean(self.data[labels == j], dim=0)

            flag = self.converge(old_center, center)

        return labels, center

def BDTF_false_ID(s_path, t_path):
    with open(s_path, "r", encoding="utf-8-sig") as fr:
        s = json.load(fr)
    false_ID = []
    for example in s:
        if len(example['pairs']) != len(example['pair_preds']):
            false_ID.append(example['ID'])
            continue
        for i in range(len(example['pairs'])):
            if example['pair_preds'][i] not in example['pairs']:
                false_ID.append(example['ID'])
                break
    with open(t_path, "w", encoding="utf-8-sig") as fr:
        json.dump(false_ID, fr)
    return false_ID

def to_BDTF(s_path, t_path):
    total_examples = []
    tokenizer = AutoTokenizer.from_pretrained("./bert-base-uncased")
    with open(s_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for index, line in enumerate(lines):
        dict = {}
        dict["ID"] = index
        line = line.strip()
        line = line.split('####')
        sentence = line[0].split()  # sentence
        raw_pairs = eval(line[1])  # triplets
        dict["sentence"] = " ".join(sentence)
        sentence = [word.lower() for word in sentence]

        encoding = tokenizer(sentence, is_split_into_words=True)
        tokens_list = tokenizer.tokenize(sentence, is_split_into_words=True)
        entities_list = []
        pairs_list = []
        aspect_list = []
        opinion_list = []
        had_aspect = []
        had_opinion = []
        for triple in raw_pairs:
            raw_aspect = triple[0]
            raw_opinion = triple[1]

            if len(raw_aspect) == 1:
                aspect_word = sentence[raw_aspect[0]]
                span = encoding.word_to_tokens(raw_aspect[0])
                aspect_tokens_span = [span[0]-1, span[1]-1]
                aspect_tokens = tokens_list[aspect_tokens_span[0]:aspect_tokens_span[1]]
                if raw_aspect not in had_aspect:
                    had_aspect.append(raw_aspect)
                    aspect_list.append(["target", aspect_tokens_span[0], aspect_tokens_span[1], str(aspect_tokens), aspect_word])
            else:
                aspect_word = ' '.join(sentence[raw_aspect[0]: raw_aspect[-1] + 1])
                start_span = encoding.word_to_tokens(raw_aspect[0])
                end_span = encoding.word_to_tokens(raw_aspect[-1])
                aspect_tokens_span = [start_span[0]-1, end_span[1]-1]
                aspect_tokens = tokens_list[aspect_tokens_span[0]:aspect_tokens_span[1]]
                if raw_aspect not in had_aspect:
                    had_aspect.append(raw_aspect)
                    aspect_list.append(["target", aspect_tokens_span[0], aspect_tokens_span[1], str(aspect_tokens), aspect_word])

            if len(raw_opinion) == 1:
                opinion_word = sentence[raw_opinion[0]]
                span = encoding.word_to_tokens(raw_opinion[0])
                opinion_tokens_span = [span[0] - 1, span[1] - 1]
                opinion_tokens = tokens_list[opinion_tokens_span[0]:opinion_tokens_span[1]]
                if raw_opinion not in had_opinion:
                    had_opinion.append(raw_opinion)
                    opinion_list.append(["opinion", opinion_tokens_span[0], opinion_tokens_span[1], str(opinion_tokens), opinion_word])
            else:
                opinion_word = ' '.join(sentence[raw_opinion[0]: raw_opinion[-1] + 1])
                start_span = encoding.word_to_tokens(raw_opinion[0])
                end_span = encoding.word_to_tokens(raw_opinion[-1])
                opinion_tokens_span = [start_span[0] - 1, end_span[1] - 1]
                opinion_tokens = tokens_list[opinion_tokens_span[0]:opinion_tokens_span[1]]
                if raw_opinion not in had_opinion:
                    had_opinion.append(raw_opinion)
                    opinion_list.append(["opinion", opinion_tokens_span[0], opinion_tokens_span[1], str(opinion_tokens), opinion_word])

            pairs_list.append([aspect_tokens_span[0], aspect_tokens_span[1], opinion_tokens_span[0], opinion_tokens_span[1], triple[2]])
        entities_list += aspect_list
        entities_list += opinion_list
        dict["entities"] = entities_list
        dict["pairs"] = pairs_list
        dict["tokens"] = str(tokens_list)
        total_examples.append(dict)
    with open(t_path, mode='w', encoding='utf-8-sig') as f:
        json.dump(total_examples, f, indent=4)

def SBN_false_ID(s_path, t_path):
    with open(s_path, "r", encoding="utf-8-sig") as fr:
        s = json.load(fr)
    false_ID = []
    for id, dict in enumerate(s):
        new = dict["new"]
        lack = dict["lack"]
        if len(new) != 0 or len(lack) != 0:
            false_ID.append(id)
    with open(t_path, "w", encoding="utf-8-sig") as fr:
        json.dump(false_ID, fr)
    return false_ID

def COMMRC_false_ID(s_path, t_path, dataset):
    gold_path = "./{}/COMMRC/COMMRC_gold.txt".format(dataset)  # true labels of the validation set
    with open(s_path, "r", encoding="utf-8") as fr:
        pre = fr.read()
    with open(gold_path, "r", encoding="utf-8") as fr:
        gold = fr.read()
    pre_set = eval(pre)
    gold_set = eval(gold)
    correct_set = gold_set & pre_set
    pre_false_set = pre_set - correct_set
    gold_false_set = gold_set - correct_set
    false_set = pre_false_set | gold_false_set
    false_list = list(false_set)
    false_ID = []
    for i in false_list:
        id = int(i.split('-')[0])
        if id not in false_ID:
            false_ID.append(id)
    with open(t_path, "w", encoding="utf-8-sig") as fr:
        json.dump(false_ID, fr)
    return false_ID

def SLGM_false_ID(s_path, t_path, dataset):
    gold_path = "./{}/SLGM/SLGM_gold.json".format(dataset)   # true labels of the validation set
    with open(gold_path, "r", encoding="utf-8") as fr:
        gold = json.load(fr)
    with open(s_path, "r", encoding="utf-8") as fr:
        s = json.load(fr)
    false_ID = []
    for index, label in enumerate(gold):
        predict = s[index][1:]
        predict.append(int(0))
        if predict != label:
            false_ID.append(index)
    with open(t_path, "w", encoding="utf-8") as fr:
        json.dump(false_ID, fr)
    return false_ID


if __name__ == "__main__":
    random.seed(2025)
    # s_name: prediction results of the model on the validation set
    # previous_path: training data n-1
    # current_path: training data n
    # k : number of cluster center points
    dataset = "14lap"
    model = "COMMRC"
    train = "train_version_0"
    k = 10
    s_name = "triples_0.5948553054662379.txt"
    t_name = "triples_0.5948553054662379"
    previous_path = "/ASTE-Data-V3/{}/train_triplets.txt".format(dataset)   # Set your absolute path
    # previous_path = "./{}/{}/{}/train_triplets_100.txt".format(dataset, model, train)
    current_path = "./{}/{}/{}/train_triplets_100.txt".format(dataset, model, train)
    if model == "BDTF":
        current_json_path = "./{}/{}/{}/train_triplets_100.json".format(dataset, model, train)


    s_path = "./{}/{}/{}/{}".format(dataset, model, train, s_name)
    t_path = "./{}/{}/{}/{}_false_id.txt".format(dataset, model, train, t_name)
    if model == "SBN":
        false_ID = SBN_false_ID(s_path, t_path)
    elif model == "BDTF":
        false_ID = BDTF_false_ID(s_path, t_path)
    elif model == "COMMRC":
        false_ID = COMMRC_false_ID(s_path, t_path, dataset)
    elif model == "SLGM":
        false_ID = SLGM_false_ID(s_path, t_path, dataset)
    print(len(false_ID))

    te_path = "./{}/val_triplets_embed.txt".format(dataset)
    with open(te_path, mode='r', encoding='utf-8') as f:
        test_lines = f.readlines()
    test_embedding = []
    for line in test_lines:
        line = line.strip()
        line = line.split("\t")
        test_embedding.append(eval(line[1]))
    test_embedding = torch.tensor(test_embedding).to(device)
    false_embedding = test_embedding[false_ID, :]

    chat_path = "./{}/chatgpt_synthetic_candidates_embed.txt".format(dataset)
    chat_used_path = "./{}/{}/{}/had_used.txt".format(dataset, model, train)  # had used synthetic samples
    with open(chat_path, mode='r', encoding='utf-8') as f:
        chat_lines = f.readlines()
    with open(chat_used_path, mode='r', encoding='utf-8') as f:
        chat_used_lines = f.readlines()
    for line in chat_used_lines:
        chat_lines.remove(line)
    chat_embedding = []
    chat_ID = []
    for line in chat_lines:
        line = line.strip()
        line = line.split("\t")
        chat_embedding.append(eval(line[1]))
        chat_ID.append(int(line[0]))
    chat_embedding = torch.tensor(chat_embedding).to(device)
    chat_ID = torch.tensor(chat_ID).to(device)

    topk_num = int(100 / k)
    _, center = K_means(false_embedding, k).forward()
    ID_list1 = []
    for i in range(k):
        point = center[i].unsqueeze(dim=0).expand_as(chat_embedding)
        dis = torch.sum((point-chat_embedding)**2, dim=1).sqrt()
        values, indices = dis.topk(topk_num)
        ID_list1.append(chat_ID[indices])
        leave_indices = [index for index in torch.arange(chat_embedding.size(0)).to(device) if index not in indices]
        chat_embedding = chat_embedding[leave_indices, :]
        chat_ID = chat_ID[leave_indices]
    ID_list2 = []
    for tensor in ID_list1:
        ID_list2.extend(tensor.cpu().numpy().tolist())
    print(len(list(set(ID_list2))))

    gpt_path = "/data_generation/{}/chatgpt_synthetic_candidates.txt".format(dataset)  # Set your absolute path
    with open(chat_path, mode='r', encoding='utf-8') as f:
        chat_lines = f.readlines()
    with open(gpt_path, mode='r', encoding='utf-8') as f:
        gpt_lines = f.readlines()
    with open(previous_path, mode='r', encoding='utf-8') as f:
        previous_lines = f.readlines()

    for id in ID_list2:
        previous_lines.append(gpt_lines[id])
    with open(current_path, mode='w', encoding='utf-8') as f:
        for line in previous_lines:
            f.writelines(line)
    ID_list2 = list(set(ID_list2))
    with open(chat_used_path, mode='a+', encoding='utf-8') as f:
        for id in ID_list2:
            f.writelines(chat_lines[id])
    if model == "BDTF":
        to_BDTF(current_path, current_json_path)






