import os
import json
from collections import defaultdict, Counter
import sys
import statistics
import copy

import Levenshtein


class AnnotationResults:
    def __init__(self, filenames):
        self.annotations = []
        for filename in filenames:
            with open(filename) as f:
                self.annotations.append(json.load(f))


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
        features = ('Grammaticality', 'Fluency', 'Meaning Preservation')
        data = self.merge_annotations(self.annotations)
        for example in data:
            for system, results in example['systems'].items():
                for annotator, annotations in results['annotators'].items():
                    for feature in features:
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


def main():
    ar = AnnotationResults(sys.argv[1:])
    ar.summarize()


if __name__ == '__main__':
    main()

