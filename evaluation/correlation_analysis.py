"""Code to compute correlations between metrics/human evaluations

There is too little data for estimating uncertainty, so that is not currently
printed.
"""

import numpy as np
import scipy.stats

automatic_scores = {
    # Table 2 in paper
    'GLEU': {
        'Uncorrected':  { 'All': 0.44, 'A': 0.29, 'B': 0.17, 'C': 0.53},
        'Granska':      { 'All': 0.47, 'A': 0.35, 'B': 0.24, 'C': 0.55},
        'MT':           { 'All': 0.57, 'A': 0.48, 'B': 0.38, 'C': 0.63},
        'GPT-3':        { 'All': 0.63, 'A': 0.60, 'B': 0.52, 'C': 0.65},
        'Human minimal':{ 'All': 1.00, 'A': 1.00, 'B': 1.00, 'C': 1.00},
        },
    # Table 3 in paper
    'Scribendi': {
        'Uncorrected':  { 'All': 0.00, 'A': 0.00, 'B': 0.00, 'C': 0.00},
        'Granska':      { 'All': 0.03, 'A': 0.08, 'B': 0.11, 'C': -0.01},
        'MT':           { 'All': 0.51, 'A': 0.57, 'B': 0.68, 'C': 0.43},
        'GPT-3':        { 'All': 0.69, 'A': 0.70, 'B': 0.83, 'C': 0.65},
        'Human minimal':{ 'All': 0.68, 'A': 0.67, 'B': 0.77, 'C': 0.65},
        }
    }

# Table 4 in paper
human_scores = {
    'Grammaticality': {
        'Granska':      { 'All': 3.00, 'A': 3.10, 'B': 2.50, 'C': 3.30},
        'MT':           { 'All': 3.30, 'A': 3.40, 'B': 3.00, 'C': 3.50},
        'GPT-3':        { 'All': 3.70, 'A': 3.80, 'B': 3.60, 'C': 3.80},
        'Human fluent': { 'All': 3.90, 'A': 3.90, 'B': 3.80, 'C': 3.90},
        'Human free':   { 'All': 3.90, 'A': 3.90, 'B': 3.90, 'C': 3.80},
        },
    'Fluency': {
        'Granska':      { 'All': 2.80, 'A': 3.00, 'B': 2.30, 'C': 3.20},
        'MT':           { 'All': 3.10, 'A': 3.20, 'B': 2.70, 'C': 3.30},
        'GPT-3':        { 'All': 3.60, 'A': 3.70, 'B': 3.40, 'C': 3.70},
        'Human fluent': { 'All': 3.80, 'A': 3.80, 'B': 3.70, 'C': 3.80},
        'Human free':   { 'All': 3.80, 'A': 3.80, 'B': 3.90, 'C': 3.80},
         },
    'Meaning preservation': {
        'Granska':      { 'All': 3.50, 'A': 3.50, 'B': 3.20, 'C': 3.70},
        'MT':           { 'All': 3.40, 'A': 3.50, 'B': 3.10, 'C': 3.60},
        'GPT-3':        { 'All': 3.40, 'A': 3.60, 'B': 3.10, 'C': 3.60},
        'Human fluent': { 'All': 3.90, 'A': 4.00, 'B': 3.90, 'C': 3.80},
        'Human free':   { 'All': 3.80, 'A': 3.80, 'B': 3.80, 'C': 3.80},
         },
    'NLD': {
        'Granska':      { 'All': 0.126, 'A': 0.119, 'B': 0.180, 'C': 0.079},
        'MT':           { 'All': 0.113, 'A': 0.095, 'B': 0.158, 'C': 0.087},
        'GPT-3':        { 'All': 0.076, 'A': 0.068, 'B': 0.112, 'C': 0.050},
        'Human fluent': { 'All': 0.034, 'A': 0.034, 'B': 0.045, 'C': 0.022},
        'Human free':   { 'All': 0.029, 'A': 0.030, 'B': 0.034, 'C': 0.025},
         },
    }

def correlate_scores(scores1, scores2, level='All'):
    common = sorted(set(scores1) & set(scores2))
    x = [scores1[s][level] for s in common]
    y = [scores2[s][level] for s in common]
    r = scipy.stats.pearsonr(x, y)
    bs = scipy.stats.BootstrapMethod(method='BCa', n_resamples=999)
    ci = r.confidence_interval(confidence_level=0.90, method=bs)
    print('Correlating', x, y, 'r =', r)
    return [r.statistic, ci.low, ci.high]


metric_order = {'Grammaticality': 0, 'Fluency': 1, 'Meaning preservation': 2,
                'NLD': 3}
print('&', ' & '.join(sorted(human_scores, key=metric_order.get)), r'\\')

for label1, scores1 in sorted(automatic_scores.items()):
    row = [label1]
    for label2, scores2 in sorted(human_scores.items(),
                                  key=lambda t: metric_order[t[0]]):
        level = 'All'
        r, low, high = correlate_scores(scores1, scores2, level)
        row.append(f'{r:.2f}')
    print(' & '.join(row), r'\\')

for label1, scores1 in sorted(human_scores.items(),
                              key=lambda t: metric_order[t[0]]):
    row = [label1]
    for label2, scores2 in sorted(human_scores.items(),
                                  key=lambda t: metric_order[t[0]]):
        if label1 == label2:
            row.append('')
            continue
        level = 'All'
        r, low, high = correlate_scores(scores1, scores2, level)
        row.append(f'{r:.2f}')
    print(' & '.join(row), r'\\')

