import argparse
import pandas as pd
import random
from pprint import pprint
import numpy as np
import sys
from rouge import Rouge 
from bert_score import BERTScorer
from tqdm import tqdm
from scipy.stats import spearmanr
from kctv.data import prepare_latex_for_eval

# hide the loading messages
import logging
import transformers
transformers.tokenization_utils.logger.setLevel(logging.ERROR)
transformers.configuration_utils.logger.setLevel(logging.ERROR)
transformers.modeling_utils.logger.setLevel(logging.ERROR)
import evaluate

bert_scorer = BERTScorer(lang="en", device="cuda:1")
rouge_scorer = Rouge()
meteor_scorer = evaluate.load('meteor')
bleu_scorer = evaluate.load("bleu")


sys.setrecursionlimit(15000)

def dummy_qual_function(ref, pred):
    return random.uniform(0, 1)

def get_rouge1_scores(ref, pred):
    if len(pred) == 0 or len(ref) == 0:
        return 0.0, 0.0
    scores = rouge_scorer.get_scores(pred, ref)
    return scores[0]['rouge-1']['r'], scores[0]['rouge-1']['p']

def get_rougeL_scores(ref, pred):
    if len(pred) == 0 or len(ref) == 0:
        return 0.0, 0.0
    scores = rouge_scorer.get_scores(pred, ref)
    return scores[0]['rouge-l']['r'], scores[0]['rouge-l']['p']

def get_bert_scores(ref, pred):
    if len(pred) == 0 or len(ref) == 0:
        return 0.0, 0.0
    P, R, F1 = bert_scorer.score([pred], [ref])
    return R.item(), P.item()

def get_meteor_scores(ref, pred):
    score = meteor_scorer.compute(predictions=[pred], references=[ref])['meteor']
    return score, score

def get_bleu_scores(ref, pred):
    if len(pred) == 0 or len(ref) == 0:
        return 0.0, 0.0

    score = bleu_scorer.compute(predictions=[pred], references=[ref])['bleu']
    return score, score


'''
refs: iterable of reference frames
preds: iterable of predicted frames
qual_func: function that takes two strings as input and returns a twp float scores (recall, precision)
'''
def get_quality_scores(refs, preds, qual_func):
    k = len(refs.columns)
    n, m = len(refs), len(preds)
    recall_scores = np.zeros((k,n,m))
    precision_scores = np.zeros((k,n,m))
    
    for k_idx in range(k):
        for r_idx in range(n):
            for p_idx in range(m):
                try:
                    r, p = qual_func(str(refs.iloc[r_idx, k_idx]), str(preds[p_idx]))
                except:
                    r, p = 0.0, 0.0
                recall_scores[k_idx, r_idx, p_idx] = r
                precision_scores[k_idx, r_idx, p_idx] = p
    return recall_scores, precision_scores

def get_sim_rankings(most_sim_to_ref, most_sim_to_pred, k, n, m):
    ref_to_pred_ranking = []
    for ki in range(k):
        ki_ref_to_pred_ranking = []
        for i in range(n):
            for j, mapping in enumerate(most_sim_to_ref[ki]):
                if i == mapping:
                    ki_ref_to_pred_ranking.append(j)
        ref_to_pred_ranking.append(ki_ref_to_pred_ranking)
    
    pred_to_ref_ranking = []
    for ki in range(k):
        ki_pred_to_ref_ranking = []
        for i in range(m):
            for j, mapping in enumerate(most_sim_to_pred[ki]):
                if i == mapping:
                    ki_pred_to_ref_ranking.append(j)
        pred_to_ref_ranking.append(ki_pred_to_ref_ranking)

    return ref_to_pred_ranking, pred_to_ref_ranking

def get_permutation_penalty(ref_to_pred_ranking, pred_to_ref_ranking, k, n, m):

    if m > 1:
        recall_penalty = max(
            [
            (spearmanr(list(range(m)), ref_to_pred_ranking[ki]).statistic + 1) / 2 for ki in range(k)
            ]
        )
    else:
        recall_penalty = 1.0
    if n > 1:
        precision_penalty =  max(
            [
            (spearmanr(list(range(n)), pred_to_ref_ranking[ki]).statistic + 1) / 2 for ki in range(k)
            ]
        )
    else:
        precision_penalty = 1.0

    return recall_penalty, precision_penalty

def score(reference_docs, predicted_docs, quality_function, quiet=False):
    r_n, p_m = len(reference_docs), len(predicted_docs)

    assert r_n == p_m

    recall_scores = np.zeros((r_n))
    precision_scores =  np.zeros((r_n))
    all_recall_quality_scores =  np.zeros((r_n))
    all_precision_quality_scores = np.zeros((r_n))
    all_recall_perm_penalties =  np.zeros((r_n))
    all_precision_perm_penalties = np.zeros((r_n))
    all_length_penalties =  np.zeros((r_n))

    quality_functions = {
        'rouge-1': get_rouge1_scores,
        'rouge-L': get_rougeL_scores,
        'bert-score': get_bert_scores,
        'meteor': get_meteor_scores,
        'bleu': get_bleu_scores
    }

    qual_func = quality_functions[quality_function]

    for doc_idx, (ref_path, pred_path) in tqdm(enumerate(zip(reference_docs, predicted_docs)), disable=quiet):
        ref_frames = pd.read_csv(ref_path.strip())
        ref_frames = ref_frames.dropna()
        pred_frames = prepare_latex_for_eval(open(pred_path.strip()).read())

        recall_quality_scores, precision_quality_scores = get_quality_scores(ref_frames, pred_frames, qual_func)


        k, n, m = recall_quality_scores.shape

        most_sim_to_ref = recall_quality_scores.argmax(axis=1)
        most_sim_to_pred = precision_quality_scores.argmax(axis=2)

        ref_to_pred_ranking, pred_to_ref_ranking = get_sim_rankings(most_sim_to_ref, most_sim_to_pred, k, n, m)

        recall_perm_penalty, precision_perm_penalty = get_permutation_penalty(ref_to_pred_ranking, pred_to_ref_ranking, k, n, m)
        length_penalty = np.exp(-np.abs(n-m)/n)

        recall_quality_score = max([recall_quality_scores[ki][list(range(n)), most_sim_to_pred].mean() for ki in range(k)])
        precision_quality_score = max([precision_quality_scores[ki][most_sim_to_ref, list(range(m))].mean() for ki in range(k)])

        recall_scores[doc_idx] = recall_quality_score * recall_perm_penalty * length_penalty
        precision_scores[doc_idx] = precision_quality_score * precision_perm_penalty * length_penalty

        all_recall_quality_scores[doc_idx] =  recall_quality_score
        all_precision_quality_scores[doc_idx] = precision_quality_score
        all_recall_perm_penalties[doc_idx] =  recall_perm_penalty
        all_precision_perm_penalties[doc_idx] = precision_perm_penalty
        all_length_penalties[doc_idx] =  length_penalty
    
    

    recall = recall_scores.mean()
    precision = precision_scores.mean()

    if (precision + recall) == 0.0:
        f1 = 0.0
    else:
        f1 = (2*precision*recall) / (precision + recall)

    avg_recall_quality_score = all_recall_quality_scores.mean()
    avg_precision_quality_score = all_precision_quality_scores.mean()
    avg__recall_perm_penalty = all_recall_perm_penalties.mean()
    avg_precision_perm_penalty = all_precision_perm_penalties.mean()
    avg_len_penalty = all_length_penalties.mean()

    final_scores = {
        'Recall': recall,
        'Precision': precision,
        'F1': f1,
        'avg_recall_quality_score': avg_recall_quality_score,
        'avg_precision_quality_score': avg_precision_quality_score,
        'avg__recall_perm_penalty': avg__recall_perm_penalty,
        'avg_precision_perm_penalty': avg_precision_perm_penalty,
        'avg_len_penalty': avg_len_penalty
    }

    return final_scores

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('quality_function', choices=['rouge-1', 'rouge-L', 'bert-score', 'meteor', 'bleu'])
    parser.add_argument('reference_doc', help='path to reference doc')
    parser.add_argument('predicted_doc', help='path to predicted doc')
    parser.add_argument('--quiet', default=False, action='store_true', help='flag to disable progress bar')

    args = parser.parse_args()
    scores = score([args.reference_doc], [args.predicted_doc], args.quality_function, quiet=args.quiet)
    pprint(scores)