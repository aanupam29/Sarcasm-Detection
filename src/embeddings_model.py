import os, utils
import data_processing as data_proc
import numpy as np

if __name__ == "__main__":
    path = os.getcwd()[:os.getcwd().rfind('/')]
    to_write_filename = path + '/stats/embeddings_tests_1mar_weighted_clean_100d.txt'
    utils.initialize_writer(to_write_filename)

    train_filename = "train.txt"
    test_filename = "test.txt"
    dict_filename = "word_list.txt"
    word_filename = "word_list_freq.txt"

    # Load the data
    x_train = utils.load_file(path + "/res/data/grammatical_clean_original_" + train_filename).split("\n")
    x_test = utils.load_file(path + "/res/data/grammatical_clean_original_" + test_filename).split("\n")

    # Make sure all words are lower-case
    x_train = [t.lower() for t in x_train]
    x_test = [t.lower() for t in x_test]

    # Load the labels
    y_train = [int(l) for l in utils.load_file(path + "/res/data/labels_" + train_filename).split("\n")]
    y_test = [int(l) for l in utils.load_file(path + "/res/data/labels_" + test_filename).split("\n")]

    # Extract just the emojis present in each tweet in each set
    x_train_emoji = data_proc.extract_emojis(x_train)
    x_test_emoji = data_proc.extract_emojis(x_test)

    # Load the deepmoji predictions for each tweet
    x_train_deepmoji = utils.get_deepmojis("data_frame_" + train_filename[:-4] + ".csv", threshold=0.05)
    x_train_deepmoji = [' '.join(e) for e in x_train_deepmoji]

    x_test_deepmoji = utils.get_deepmojis("data_frame_" + test_filename[:-4] + ".csv", threshold=0.05)
    x_test_deepmoji = [' '.join(e) for e in x_test_deepmoji]

    # Get the concatenation of present and predicted emojis
    x_train_all_emojis = [x_train_deepmoji[i] if x_train_emoji[i] == ''
                          else x_train_emoji[i] + ' ' + x_train_deepmoji[i] for i in range(len(x_train_emoji))]
    x_test_all_emojis = [x_test_deepmoji[i] if x_test_emoji[i] == ''
                         else x_test_emoji[i] + ' ' + x_test_deepmoji[i] for i in range(len(x_test_emoji))]

    # Load the embeddings
    embedding_dim = 300
    random_word2vec_map = utils.build_random_word2vec(x_train, embedding_dim=embedding_dim, variance=1)
    word2vec_map = utils.load_vectors(filename='glove.6B.%dd.txt' % embedding_dim)
    emoji2vec_map = utils.load_vectors(filename='emoji_embeddings_%dd.txt' % embedding_dim)

    # Setting for the embeddings
    init_unk = True
    var = None
    weighted = True

    # Get embeddings for train set
    x_train_rand_word_emb = utils.get_tweets_embeddings(x_train, random_word2vec_map, embedding_dim,
                                                        init_unk=init_unk, variance=var, weighted_average=weighted)
    x_train_word_emb = utils.get_tweets_embeddings(x_train, word2vec_map, embedding_dim,
                                                   init_unk=init_unk, variance=var, weighted_average=weighted)
    x_train_emoji_emb = utils.get_tweets_embeddings(x_train_emoji, emoji2vec_map, embedding_dim,
                                                    init_unk=init_unk, variance=var, weighted_average=weighted)
    x_train_deepemoji_emb = utils.get_tweets_embeddings(x_train_deepmoji, emoji2vec_map, embedding_dim,
                                                        init_unk=init_unk, variance=var, weighted_average=weighted)
    x_train_all_emoji_emb = utils.get_tweets_embeddings(x_train_all_emojis, emoji2vec_map, embedding_dim,
                                                        init_unk=init_unk, variance=var, weighted_average=weighted)

    # Get embeddings for test set
    x_test_rand_word_emb = utils.get_tweets_embeddings(x_test, random_word2vec_map, embedding_dim,
                                                       init_unk=init_unk, variance=var, weighted_average=weighted)
    x_test_word_emb = utils.get_tweets_embeddings(x_test, word2vec_map, embedding_dim,
                                                  init_unk=init_unk, variance=var, weighted_average=weighted)
    x_test_emoji_emb = utils.get_tweets_embeddings(x_test_emoji, emoji2vec_map, embedding_dim,
                                                   init_unk=init_unk, variance=var, weighted_average=weighted)
    x_test_deepemoji_emb = utils.get_tweets_embeddings(x_test_deepmoji, emoji2vec_map, embedding_dim,
                                                       init_unk=init_unk, variance=var, weighted_average=weighted)
    x_test_all_emoji_emb = utils.get_tweets_embeddings(x_test_all_emojis, emoji2vec_map, embedding_dim,
                                                       init_unk=init_unk, variance=var, weighted_average=weighted)

    # Obtain features by concatenating word embeddings with all emoji embeddings
    x_train_features_concat = []
    for t, e in zip(x_train_word_emb, x_train_all_emoji_emb):
        x_train_features_concat.append(np.concatenate((t, e), axis=0))

    x_test_features_concat = []
    for t, e in zip(x_test_word_emb, x_test_all_emoji_emb):
        x_test_features_concat.append(np.concatenate((t, e), axis=0))

    # Obtain features by adding together the word embeddings with all emoji embeddings
    x_train_features_sum = []
    for t, e in zip(x_train_word_emb, x_train_all_emoji_emb):
        x_train_features_sum.append(t + e)

    x_test_features_sum = []
    for t, e in zip(x_test_word_emb, x_test_all_emoji_emb):
        x_test_features_sum.append(t + e)

    print("\nShape of concatenated train features: ", np.array(x_train_features_concat).shape)
    print("Shape of concatenated test features: ", np.array(x_test_features_concat).shape)
    print("Shape of summed train features: ", np.array(x_train_features_sum).shape)
    print("Shape of summed test features: ", np.array(x_test_features_sum).shape)

    features = {'Random word embeddings': [x_train_rand_word_emb, x_test_rand_word_emb],
                'Just word embeddings': [x_train_word_emb, x_test_word_emb],
                'Just present emojis': [x_train_emoji_emb, x_test_emoji_emb],
                'Just deepmojis': [x_train_deepemoji_emb, x_test_deepemoji_emb],
                'All emojis': [x_train_all_emoji_emb, x_test_all_emoji_emb],
                'Words + all emojis concat': [x_train_features_concat, x_test_features_concat],
                'Words + all emojis summed': [x_train_features_sum, x_test_features_sum]
                }
    import time
    for k, v in features.items():
        print("===================================================================")
        print("\nNow testing: %s\n" % k)
        print("===================================================================")
        start = time.time()
        utils.run_models(v[0], y_train, v[1], y_test)
        end = time.time()
        print("Completion time of the ML model: %.3f s = %.3f min" % ((end - start), (end - start) / 60.0))
