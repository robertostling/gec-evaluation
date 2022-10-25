import argparse
import os
import json
from collections import defaultdict, Counter
from operator import itemgetter
import itertools
import sys
import statistics
import copy

import Levenshtein

FEATURES = ('Grammaticality', 'Fluency', 'Meaning Preservation')

class AnnotationResults:
    def __init__(self, filenames):
        self.annotations = []
        for filename in filenames:
            with open(filename) as f:
                self.annotations.append(json.load(f))

        self.merged_data = self.merge_annotations(self.annotations)


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


    def get_scores(self):
        system_measure_counts = defaultdict(lambda: defaultdict(Counter))
        system_metrics = defaultdict(lambda: defaultdict(list))
        for example in self.merged_data:
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


    def summarize(self):
        system_measure_counts, system_metrics = self.get_scores()
        for system, measure_counts in system_measure_counts.items():
            print(system)
            for measure, counts in sorted(measure_counts.items()):
                n_sum = sum(n*c for n, c in counts.items() if n != 0)
                total = sum(c   for n, c in counts.items() if n != 0)
                print(f'  {measure:24s} {n_sum/total:.1f} (n={total})')
            metrics = system_metrics[system]
            for metric, values in sorted(metrics.items()):
                mean = statistics.mean(values)
                print(f'  {metric:24s} {mean:.2g} (n={len(values)})')
            print()


    def compare_differences(self, show_all=True):
        for example in self.merged_data:
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


def main():
    parser = argparse.ArgumentParser('Analyze annotation files')
    parser.add_argument(
            '--only-differences', action='store_true',
            help='When comparing annotators, only show different annotations')
    parser.add_argument(
            '--action', default='summarize',
            choices=('compare', 'summarize'),
            help='Action to perform: compare summarize [default]')
    parser.add_argument(
            'input', nargs='+')
    args = parser.parse_args()

    ar = AnnotationResults(args.input)
    if args.action == 'summarize':
        ar.summarize()
    elif args.action == 'compare':
        ar.compare_differences(show_all=not args.only_differences)
    else:
        raise ValueError()


if __name__ == '__main__':
    main()

