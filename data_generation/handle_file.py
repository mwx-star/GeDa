import string
import random

def rewrite(t_path, s_path):
    sentiment_dict = {'positive': "POS", 'negative': "NEG", 'neutral': "NEU"}
    with open(t_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(s_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if "####" not in line:
                continue
            line = line.strip()
            line = line.split('####')
            sentence = line[0].split()[1:]  # sentence
            print(line)
            triplet = eval(line[1])  # triplets

            triplet_list = []
            for triple in triplet:
                triplet_list.append((triple[0], triple[1], sentiment_dict[triple[-1]]))
            save_line = " ".join(sentence) + "####" + str(triplet_list) + "\n"
            f.writelines(save_line)


def filter_v1(t_path, s_path):
    lap_list = ["laptop", "Laptop", "notebook", "Notebook", "computer", "Computer", "machine", "Machine", "device", "Device"]
    # res_list = ["restaurant", "Restaurant"]
    with open(t_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(s_path, 'w', encoding='utf-8') as f:
        for line in lines:
            raw_line = line
            line = line.strip()
            line = line.split('####')
            sentence = line[0]  # sentence
            print(line)
            triplet = eval(line[1])  # triplets
            flag = True
            for triple in triplet:
                if len(triple) != 3:
                    flag = False
                    break
                if triple[0] not in sentence:
                    flag = False
                    break
                if triple[0] in res_list :
                    flag = False
                    break
                if triple[1] not in sentence:
                    flag = False
                    break
            if flag:
                f.writelines(raw_line)

def punctuation(t_path, s_path):
    with open(t_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(s_path, 'w', encoding='utf-8') as f:
        for s_index, line in enumerate(lines):
            line = line.strip()
            line = line.split('####')
            sentence = line[0]  # sentence
            triplet = eval(line[1])  # triplets
            if "n't" in sentence:
                A = sentence.count("'")
                B = sentence.count("n't")
                if A != B:
                    sentence = sentence.split()
                    save_line = " ".join(sentence) + "####" + str(triplet) + "\n"
                    f.writelines(save_line)
                    print("需手动修改ID：", s_index + 1)
                    continue
            sentence_copy = sentence
            punctuation_list = []
            for index, c in enumerate(sentence):
                if c == "$":
                    if c not in punctuation_list:
                        punctuation_list.append(c)
                        sentence = sentence.replace(c, c + " ")
                    continue
                if c == "'" and sentence_copy[index-1:index+2] == "n't":
                    if "n't" not in punctuation_list:
                        punctuation_list.append("n't")
                        sentence = sentence.replace("n't", " n't")
                    continue
                if c in string.punctuation:
                    if c not in punctuation_list:
                        punctuation_list.append(c)
                        sentence = sentence.replace(c, " " + c)
            sentence = sentence.split()
            save_line = " ".join(sentence) + "####" + str(triplet) + "\n"
            f.writelines(save_line)

def word_to_span_gpt(s_path, t_path):
    with open(s_path, 'r', encoding='utf-8') as f:
        s_lines = f.readlines()

    with open(t_path, 'w', encoding='utf-8') as f:
        for index, s_line in enumerate(s_lines):
            s_line = s_line.strip()
            s_line = s_line.split('####')
            s_sentence = s_line[0].split()  # sentence
            s_raw_pairs = eval(s_line[1])  # triplets

            triple_list = []
            for s_triple in s_raw_pairs:
                aspect_span = None
                opinion_span = None
                aspect_word = s_triple[0].split()
                opinion_word = s_triple[1].split()
                if len(aspect_word) == 1:
                    for i, word in enumerate(s_sentence):
                        if aspect_word[0] == word:
                            aspect_span = [i]
                            if s_sentence.count(word) > 1:
                                print("aspect重复出现句子ID：", index+1)
                            break
                else:
                    for i, word in enumerate(s_sentence):
                        if aspect_word[0] == word:
                            if aspect_word == s_sentence[i:i+len(aspect_word)]:
                                aspect_span = [j for j in range(i, i+len(aspect_word))]
                                break

                if len(opinion_word) == 1:
                    for i, word in enumerate(s_sentence):
                        if opinion_word[0] == word:
                            opinion_span = [i]
                            if s_sentence.count(word) > 1:
                                print("opinion重复出现句子ID：", index+1)
                            break
                else:
                    for i, word in enumerate(s_sentence):
                        if opinion_word[0] == word:
                            if opinion_word == s_sentence[i:i+len(opinion_word)]:
                                opinion_span = [j for j in range(i, i+len(opinion_word))]
                                break
                if aspect_span != None and opinion_span != None:
                    triple_list.append((aspect_span, opinion_span, s_triple[2]))
                else:
                    print("出错句子ID：", index+1)
                    continue

            line = " ".join(s_sentence) + "####" + str(triple_list) + "\n"
            f.writelines(line)

def remove_duplicate(s_path):
    with open(s_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for ex_index, line in enumerate(lines):
        line = line.strip()
        line = line.split('####')
        sentence = line[0].split()  # sentence
        raw_pairs = eval(line[1])  # triplets

        for s_triple in raw_pairs:
            aspect_count = 0
            opinion_count = 0
            aspect_word = s_triple[0].split()
            opinion_word = s_triple[1].split()
            if len(aspect_word) != 1:
                for i, word in enumerate(sentence):
                    if aspect_word[0] == word:
                        if aspect_word == sentence[i:i + len(aspect_word)]:
                            aspect_count += 1

            if len(opinion_word) != 1:
                for i, word in enumerate(sentence):
                    if opinion_word[0] == word:
                        if opinion_word == sentence[i:i + len(opinion_word)]:
                            opinion_count += 1

            if aspect_count > 1 or opinion_count > 1:
               print("重复ID：", ex_index+1)
               break

def span_to_word(s_path, t_path):
    with open(s_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    with open(t_path, 'w', encoding='utf-8') as f:
        for ex_index, line in enumerate(lines):
            line = line.strip()
            line = line.split('####')
            sentence = line[0].split()  # sentence
            raw_pairs = eval(line[1])  # triplets

            triple_list = []
            for triple in raw_pairs:
                raw_aspect = triple[0]
                raw_opinion = triple[1]
                if len(raw_aspect) == 1:
                    aspect_word = sentence[raw_aspect[0]]
                else:
                    aspect_word = ' '.join(sentence[raw_aspect[0]: raw_aspect[-1] + 1])
                if len(raw_opinion) == 1:
                    opinion_word = sentence[raw_opinion[0]]
                else:
                    opinion_word = ' '.join(sentence[raw_opinion[0]: raw_opinion[-1] + 1])
                triple_word = (aspect_word, opinion_word, triple[2]) # 原始
                triple_list.append(triple_word)
            line = " ".join(sentence) + "####" + str(triple_list) + "\n"
            f.writelines(line)

if __name__ == "__main__":
    save_path = "./14lap/chatgpt_synthetic_candidates"

    rewrite("./gpt_3.5_turbo_data.txt", "./14_lap_data_rewrite.txt")
    filter_v1("./14_lap_data_rewrite.txt", "./14_lap_data_filter.txt")
    punctuation("./14_lap_data_filter.txt", "./14_lap_data_punctuation.txt")
#------------------- Check for triples that need to be modified after processing punctuation marks -------------
# Manual modification
    # with open("./14_lap_data_punctuation.txt", 'r', encoding='utf-8') as f:
    #     lines = f.readlines()
    # for index, line in enumerate(lines):
    #     line = line.strip()
    #     line = line.split('####')
    #     sentence = line[0]  # sentence
    #     triplet = eval(line[1])  # triplets
    #
    #     for triple in triplet:
    #         if triple[0] not in sentence:
    #             print("Aspect need modified ID：", index+1)
    #             break
    #         if triple[1] not in sentence:
    #             print("Opinion need modified ID：", index+1)
    #             break

#------------------------------- Check for correct and incorrect aspects and opinion ------------------------------------------
    with open("./14_lap_data_punctuation.txt", 'r', encoding='utf-8') as f:
        chatgpt_triplets = f.readlines()

    print(len(chatgpt_triplets))
    chatgpt_triplets_clean = []
    for line in chatgpt_triplets:
        raw_line = line
        flag = True
        line = line.strip()
        line = line.split('####')
        sentence = line[0].split()  # sentence
        triplet = eval(line[1])  # triplets
        for triple in triplet:
            if len(triple[0].split()) == 1:
                if triple[0] not in sentence:
                    flag = False
                    break
            if len(triple[1].split()) == 1:
                if triple[1] not in sentence:
                    flag = False
                    break
        if flag:
            chatgpt_triplets_clean.append(raw_line)
    print(len(chatgpt_triplets_clean))

    with open("./14lap/seed_samples.txt", 'r', encoding='utf-8') as f:
        seed_samples = f.readlines()

    total_sentences = []
    for line in seed_samples:
        line = line.strip()
        line = line.split('####')
        sentence = line[0]
        total_sentences.append(sentence)

    end = []
    with open("./14_lap_data_correct.txt", 'w', encoding='utf-8') as f:
        for line in chatgpt_triplets_clean:
            raw_line = line
            line = line.strip()
            line = line.split('####')
            sentence = line[0]
            if sentence in total_sentences:
                continue
            end.append(raw_line)
            f.writelines(raw_line)
    print(len(end))

#----------------------------------- Remove sentences with unmarked aspects ------------------------
    all_aspect = []
    all_opinion = []
    with open("./14_lap_data_correct.txt", 'r', encoding='utf-8') as f:
        gpt_lines = f.readlines()
    with open("./14lap/train_triplets_word.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        line = line.split('####')
        raw_pairs = eval(line[1])  # triplets
        for triple in raw_pairs:
            all_aspect.append(triple[0])
            all_opinion.append(triple[1])
    with open("./14lap/test_triplets_word.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        line = line.split('####')
        raw_pairs = eval(line[1])  # triplets
        for triple in raw_pairs:
            all_aspect.append(triple[0])
            all_opinion.append(triple[1])
    with open("./14lap/val_triplets_word.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        line = line.split('####')
        raw_pairs = eval(line[1])  # triplets
        for triple in raw_pairs:
            all_aspect.append(triple[0])
            all_opinion.append(triple[1])
    all_aspect = list(set(all_aspect))
    all_opinion = list(set(all_opinion))

    reserve_data = []
    for i, line in enumerate(gpt_lines):
        raw_line = line
        flag = True
        line = line.strip()
        line = line.split('####')
        sentence = line[0].split()  # sentence
        raw_pairs = eval(line[1])  # triplets

        line_aspect = []
        line_opinion = []
        for triple in raw_pairs:
            line_aspect.append(triple[0])
            line_opinion.append(triple[1])
        aspect_word = " ".join(line_aspect).split()
        opinion_word = " ".join(line_opinion).split()
        all_word = aspect_word + opinion_word
        all_word = list(set(all_word))
        for word in all_word:
            for _ in range(sentence.count(word)):
                sentence.remove(word)

        sentence_list = sentence
        sentence = " ".join(sentence)

        for aspect in all_aspect:
            if len(aspect.split()) == 1:
                if aspect in sentence_list:
                    flag = False
                    break
            elif aspect in sentence:
                flag = False
                break

        if flag:
            reserve_data.append(raw_line)
    print(len(gpt_lines))
    print(len(reserve_data))
    with open("./14_lap_data_word.txt", 'w', encoding='utf-8') as f:
        for line in reserve_data:
            f.writelines(line)

#---------------------- judging whether the same aspect has different polarities ----------------------------
# Manual modification
#     with open("./14_lap_data_word.txt", 'r', encoding='utf-8') as f:
#         gpt_lines = f.readlines()
#     for i, line in enumerate(gpt_lines):
#         line = line.strip()
#         line = line.split('####')
#         sentence = line[0].split()  # sentence
#         raw_pairs = eval(line[1])  # triplets
#         dict ={}
#         if len(raw_pairs) == 1:
#             continue
#         for triple in raw_pairs:
#             if triple[0] not in dict:
#                 dict[triple[0]] = triple[2]
#                 continue
#             if triple[2] != dict[triple[0]]:
#                 print("多极性ID：", i+1)

#--------------------------------------------------------------------------------
    # remove_duplicate("./14_lap_data_word.txt")          # Manual modification
    word_to_span_gpt("./14_lap_data_word.txt", save_path)