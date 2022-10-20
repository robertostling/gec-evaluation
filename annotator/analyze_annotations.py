import os
import json
from collections import defaultdict, Counter
import sys


class AnnotationResults:
    def __init__(self, filenames):
        self.annotations = []
        for filename in filenames:
            with open(filename) as f:
                self.annotations.append(json.load(f))


    def get_scores(self):
        # TODO: include GLEU for system_prediction wrt corrected_prediction?
        system_measure_counts = defaultdict(lambda: defaultdict(Counter))
        features = ('Grammaticality', 'Fluency', 'Meaning Preservation')
        for metadata in self.annotations:
            data = metadata['data']
            for example in data:
                for system, results in example['systems'].items():
                    for annotator, annotations in results['annotators'].items():
                        for feature in features:
                            if feature in annotations:
                                n = annotations[feature]
                                system_measure_counts[system][feature][n] += 1
        return system_measure_counts


    def summarize(self):
        for system, measure_counts in self.get_scores().items():
            print(system)
            for measure, counts in sorted(measure_counts.items()):
                n_sum = sum(n*c for n, c in counts.items() if n != 0)
                total = sum(c   for n, c in counts.items() if n != 0)
                print(f'  {measure:24s} {n_sum/total:.1f} (n={total})')
            print()


def main():
    ar = AnnotationResults(sys.argv[1:])
    ar.summarize()


if __name__ == '__main__':
    main()

