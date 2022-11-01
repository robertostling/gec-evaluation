# Guidelines for generating paraphrases

The goal of generating paraphrases is to simulate a "perfect" grammatical
error correction (GEC) system. In this context, perfection means that the
highest score should be reached for grammaticality, fluency and meaning
preservation. These are described in detail in the
[guidelines for evaluating GEC systems](./GUIDELINES.md).

Paraphrases are generated sentence by sentence, based on two versions of the
same sentence:

1. The original sentence, from a student learning Swedish.
2. The minimally corrected version of that sentence, from the SweLL project.

Note that sentence (2) is *not* necessarily perfect. It should be grammatical
(although occasional mistakes exist), and by definition it preserves the
meaning since we use this version to define the "intended meaning" of the
sentence. However, it is often not fluent, because the annotator from the
SweLL project were instructed to change as little as possible to achieve a
grammatically correct sentence with what they believe to be the intended
meaning.

For example, consider the following sentence:

* Original: Du kan ringa och bjuda honom på en fin restaurang för en särlek möte och där kan ni prata med varandra mer och mer !
* SweLL corrected: Du kan ringa och bjuda honom på en fin restaurang för ett kärleksmöte , och där kan ni prata med varandra mer och mer !

While grammatically correct, there are several non-idiomatic phrases that
makes the sentence unlikely to be produced by a native speaker. For instance,
the meaning of "kärleksmöte" (love meeting) is clear enough in context, but 
one would typically use a more established term like "dejt" (date).
The "mer and mer" (more and more) at the end does not fit the described
situation very well, one could for instance simply use "mer" instead. We could
imagine multiple ways of paraphrasing this sentence, for instance:

* Suggestion A: Du kan ringa och bjuda in honom på en dejt på en fin
  restaurang , väl där kan ni prata mer med varandra .
* Suggestion B: Du kan ringa och bjuda honom på dejt på en fin restaurang ,
  och där kan ni prata mer med varandra .

Both alternatives mean the same thing (in my opinion -- but this can be
discussed), and are grammatical and fluent. However, suggestion B is preferred
in this case because it is more similar to the original, without being
significantly less grammatical or fluent, or diverging in meaning.

Another example:

* Original: Man kan bjöda kolleger för fika eftersom det är trevlig .
* SweLL corrected: Du kan bjuda kolleger på fika eftersom det är trevligt .
* Suggestion A: Det är trevligt att bjuda sina kollegor på fika , därför kan du göra det .
* Suggestion B: Du kan bjuda dina kollegor på fika , det är trevligt .

Here, suggestion B would be a reasonable choice since it changes the sentence
structure less than suggestion A.

