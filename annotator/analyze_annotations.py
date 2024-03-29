import argparse
import os
import json
from collections import defaultdict, Counter
from operator import itemgetter
import itertools
import sys
import statistics
import copy

import numpy as np
import Levenshtein

FEATURES = ('Grammaticality', 'Fluency', 'Meaning Preservation')

# OK, I give up, sklearn also has weighted kappa
#def kappa(confusion):
#    sum1 = Counter()
#    sum2 = Counter()
#    for (v1, v2), c in confusion.items():
#        sum1[v1] += c
#        sum2[v2] += c
#    N = sum(confusion.values())
#    p_e = sum(nk1*sum2.get(v, 0) for v, nk1 in sum1.items()) / (N*N)
#    c_agree = sum(c for (v1, v2), c in confusion.items() if v1 == v2)
#    p_o = c_agree / N
#    return 1 - (1-p_o)/(1-p_e)


def kappa(confusion, weights='linear'):
    import sklearn.metrics
    labels1 = []
    labels2 = []
    for (v1, v2), c in confusion.items():
        for _ in range(c):
            labels1.append(v1)
            labels2.append(v2)
    return sklearn.metrics.cohen_kappa_score(
            labels1, labels2, weights=weights)


# TOOD: a more suitable metric might be Levenshtein distance that allows for
# jumps (with some cost) at word boundaries. Maybe this can be relatively
# cheaply implemented using existing LD for pairwise token comparisons, then
# searching through that similarity matrix.
# Problem with that approach, will not handle split/merged words well.
# Even restricting to word boundaries could be problematic in (rare) cases,
# e.g. vattenhav <-> havsvatten
# Cheaper alternative would be character n-gram overlap
def nld(s1, s2):
    d = Levenshtein.distance(s1, s2)
    return d / max(len(s1), len(s2))


class AnnotationResults:
    def __init__(self, all_filenames):
        file_groups = [
                list(group) for k, group in itertools.groupby(
                    all_filenames, lambda filename: filename != ':') if k]

        self.groups = []
        for filenames in file_groups:
            annotations = []
            for filename in filenames:
                with open(filename) as f:
                    annotations.append(json.load(f))
            data = self.merge_annotations(annotations)
            self.groups.append((annotations, data))


    def merge_annotations(self, annotations):
        merged = copy.deepcopy(annotations[0]['data'])
        merged_sentences = [(example['original'], example['reference'])
                            for example in merged]
        for metadata in annotations[1:]:
            data = metadata['data']
            data_sentences = [(example['original'], example['reference'])
                              for example in data]
            if merged_sentences != data_sentences:
                raise ValueError('Attempting to merge annotations of '
                                 'different data')
            for merged_example, data_example in zip(merged, data):
                for system, merged_results in merged_example['systems'].items():
                    if system in data_example['systems']:
                        data_results = data_example['systems'][system]
                        for annotator, annotations in \
                                data_results['annotators'].items():
                            if annotator in merged_results['annotators']:
                                raise ValueError(
                                        f'Annotator {annotator} present in '
                                        'both annotation sets')
                            merged_results['annotators'][annotator] = \
                                    annotations

        return merged


    def get_pairwise_distances(self, metric=nld, filename=None, verbose=False):
        import sklearn.manifold
        from matplotlib import pyplot as plt
        from matplotlib.lines import Line2D
        distances = defaultdict(list)
        names = set()
        for _, data in self.groups:
            for example in data:
                versions = {
                        'original': example['original'],
                        'SweLL': example['reference'],
                        }
                for system, results in example['systems'].items():
                    versions[system] = results['output']
                    for annotator, annotations in results['annotators'].items():
                        if 'corrected' in annotations:
                            version = f"{system}+{annotator}"
                            versions[version] = annotations['corrected']
                if verbose:
                    for v, s in sorted(versions.items(), key=itemgetter(0)):
                        print(v, s)
                    print()
                names |= set(versions.keys())
                for (v1, s1), (v2, s2) in itertools.combinations(
                        sorted(versions.items(), key=itemgetter(0)), 2):
                    distances[(v1, v2)].append(metric(s1, s2))

        names = sorted(names)
        for (v1, v2), ds in list(distances.items()):
            assert (v2, v1) not in distances
            distances[(v2, v1)] = ds

        # Not currently used, but could be used to check for missing data
        # n_comparisons_set = set(len(distances[(v1, v2)])
        #         for v1 in names for v2 in names
        #         if v1 != v2)

        name_parent = {}
        name_label = {}
        name_ls = {}
        name_color = {}
        annotator_alias = {'katarina': 'ann1', 'robert': 'ann2'}
        system_alias = {'s2': 'GPT-3', 'granska': 'Granska', 'mt-base': 'MT',
                        'mm': 'fluent', 'mw': 'free', 'mt': 'MT'}
        for name in names:
            if '+' in name:
                system, annotator = name.split('+')
                # Use visual coding instead
                #name_label[name] = annotator_alias[annotator]
                name_ls[name] = '--'
                name_color[name] = 'orange' if name == 'robert' else  'cyan'
                name_parent[name] = system
            elif name == 'original':
                name_label[name] = name
            elif name == 'SweLL':
                name_parent[name] = 'original'
                name_label[name] = 'grammatical'
                name_ls[name] = ':'
                name_color[name] = 'magenta'
            elif name == 'mystery':
                name_parent[name] = 'SweLL'
                name_label[name] = 'fluent'
            elif name == 'mm':
                name_parent[name] = 'SweLL'
                name_label[name] = 'fluent'
                name_color[name] = 'blue'
                name_ls[name] = ':'
            elif name == 'mw':
                name_parent[name] = 'SweLL'
                name_label[name] = 'free'
                name_color[name] = 'red'
                name_ls[name] = ':'
            else:
                name_parent[name] = 'original'
                name_label[name] = system_alias[name]

        m = [[np.mean(distances[(v1, v2)]) if (v1, v2) in distances else 0.0
              for v2 in names]
             for v1 in names]
        mds = sklearn.manifold.MDS(
                n_components=2, metric=True, dissimilarity='precomputed',
                n_init=100, max_iter=5000, eps=1e-5)
        u = mds.fit_transform(m)
        print(np.round(m, 2))
        print(names)
        #print(u)
        plt.scatter(u[:, 0], u[:, 1])
        name_vector = dict(zip(names, u))

        for name, p in name_vector.items():
            parent = name_parent.get(name)
            if name in name_label:
                plt.annotate(name_label[name], p)
            if parent is not None:
                q = name_vector[parent]
                plt.plot([q[0], p[0]], [q[1], p[1]],
                        color=name_color.get(name, 'black'),
                        linestyle=name_ls.get(name, '-'))
                #plt.arrow(q[0], q[1], p[0]-q[0], p[1]-q[1],
                #        length_includes_head=True, head_width=0,
                #        head_length=0)


        custom_lines = [Line2D([0], [0], ls='-'),
                        Line2D([0], [0], ls='--'),
                        Line2D([0], [0], ls=':')]
        plt.legend(custom_lines, [
            'GEC transformation',
            'Human post-GEC correction',
            'Human normalization'])

        if filename is not None:
            plt.savefig(filename)
        plt.show()


    def get_scores(self):
        system_measure_counts = defaultdict(lambda: defaultdict(Counter))
        system_metrics = defaultdict(lambda: defaultdict(list))
        for _, data in self.groups:
            for example in data:
                for system, results in example['systems'].items():
                    for annotator, annotations in results['annotators'].items():
                        for feature in FEATURES:
                            if feature in annotations:
                                n = annotations[feature]
                                system_measure_counts[system][feature][n] += 1
                        if 'corrected' in annotations:
                            s1 = results['output']
                            s2 = annotations['corrected']
                            ld = Levenshtein.distance(s1, s2)
                            nld = ld / max(len(s1), len(s2))
                            system_metrics[system]['NLD'].append(nld)
        return system_measure_counts, system_metrics


    def summarize(self, verbose=False):
        system_measure_counts, system_metrics = self.get_scores()
        for system, measure_counts in system_measure_counts.items():
            print(system)
            for measure in FEATURES:
                counts = measure_counts[measure]
            #for measure, counts in sorted(measure_counts.items()):
                n_sum = sum(n*c for n, c in counts.items() if n != 0)
                total = sum(c   for n, c in counts.items() if n != 0)
                n_sum_all = sum(n*c for n, c in counts.items())
                total_all = sum(c   for n, c in counts.items())
                print(f'  {measure:24s} {n_sum/total:.1f} '
                      f'(n={total}+'
                      f'{counts.get(0, 0)} "other")   '
                      f'{counts[4]:3d} {counts[3]:3d} '
                      f'{counts[2]:3d} {counts[1]:3d} '
                      f'({counts[0]}; {n_sum_all/total_all:.1f})')
            metrics = system_metrics[system]
            for metric, values in sorted(metrics.items()):
                mean = statistics.mean(values)
                print(f'  {metric:24s} {mean:.3f} (n={len(values)})')
            print()


    def compare_differences(self, show_all=True):
        for _, data in self.groups:
            confusion_matrices = defaultdict(lambda: defaultdict(Counter))
            for example in data:
                original = example['original']
                reference = example['reference']
                for system, results in example['systems'].items():
                    output = results['output']
                    annotators = sorted(results['annotators'].items(),
                                        key=itemgetter(0))

                    corrections = [
                            annotation['corrected']
                            for _, annotation in annotators]
                    ratings = [
                            tuple(annotation[feature] for feature in FEATURES)
                            for _, annotation in annotators]

                    for (name1, ann1), (name2, ann2) in itertools.combinations(
                        annotators, 2):
                        for feature in FEATURES:
                            ns = (name1, name2)
                            vs = (ann1[feature], ann2[feature])
                            confusion_matrices[ns][feature][vs] += 1

                    if show_all or len(set(corrections)) > 1 or len(set(ratings)) > 1:
                        print(f'{system:10s} {output}')
                        print(f'{"reference":10s} {reference}')
                        print(f'{"student":10s} {original}')

                    if show_all or len(set(corrections)) > 1:
                        for annotator, annotation in annotators:
                            corr = annotation['corrected']
                            print(f'{annotator:10s} {corr}')
                        print()

                    if show_all or len(set(ratings)) > 1:
                        for (annotator, _), rating in zip(annotators, ratings):
                            print(f'{annotator:10s} G{rating[0]} F{rating[1]} '
                                  f'M{rating[2]}')
                        print()

                    if show_all or len(set(corrections)) > 1 or len(set(ratings)) > 1:
                        print('-'*72)

            for (name1, name2), feature_confusion in confusion_matrices.items():
                print(f'Confusion matrices for {name1} vs {name2}')
                for feature, confusion in sorted(feature_confusion.items(),
                        key=itemgetter(0)):
                    print(f'    {feature}')
                    m = np.zeros((5, 5), dtype=int)
                    for (i, j), c in confusion.items():
                        m[i, j] = c
                    print(m)
                    print(f"    LWK = {kappa(confusion):.4g}")
                    print(f"    QWK = {kappa(confusion, 'quadratic'):.4g}")
                    print()

def main():
    parser = argparse.ArgumentParser('Analyze annotation files')
    parser.add_argument(
            '--only-differences', action='store_true',
            help='When comparing annotators, only show different annotations')
    parser.add_argument(
            '--verbose', '-v', action='store_true',
            help='More verbose output')
    parser.add_argument(
            '--action', default='summarize',
            choices=('compare', 'summarize', 'pairwise'),
            help='Action to perform: compare pairwise summarize [default]')
    parser.add_argument(
            '-o', '--output', default=None, metavar='FILE',
            help='File to write output figure to')
    parser.add_argument(
            'input', nargs='+',
            help='JSON files to analyze, grouped by :')
    args = parser.parse_args()

    ar = AnnotationResults(args.input)
    if args.action == 'summarize':
        ar.summarize(verbose=args.verbose)
    elif args.action == 'compare':
        ar.compare_differences(show_all=not args.only_differences)
    elif args.action == 'pairwise':
        ar.get_pairwise_distances(filename=args.output, verbose=args.verbose)
    else:
        raise ValueError()


if __name__ == '__main__':
    main()

