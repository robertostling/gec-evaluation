import os
import json
import glob
from collections import defaultdict, Counter
import statistics


class AnnotationResults:
    def __init__(self, directory):
        self.annotations = {}
        filenames = glob.glob(os.path.join(directory, '*.json'))
        for filename in filenames:
            annotator = os.path.splitext(os.path.basename(filename))[0]
            with open(filename) as f:
                self.annotations[annotator] = json.load(f)


    def get_scores(self):
        # TODO: include GLEU for system_prediction wrt corrected_prediction?
        system_measure_counts = defaultdict(lambda: defaultdict(Counter))
        features = ('Grammaticality', 'Fluency', 'Meaning Preservation')
        for annotator, annotations in self.annotations.items():
            for annotation in annotations:
                for feature in features:
                    system = annotation['system']
                    n = int(annotation[feature][0])
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
    import sys
    import pprint
    ar = AnnotationResults(sys.argv[1])
    ar.summarize()


if __name__ == '__main__':
    main()

