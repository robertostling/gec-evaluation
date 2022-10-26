# Annotation procedure

For guidelines on how to assign scores, please read
[the annotation guidelines](GUIDELINES.md).

## Annotating an example

When a new screen is presented, the following procedure is recommended.

1. Read through the sentences. These are the outputs of different GEC systems,
   presented in random order. Ideally they should all mean the same thing, but
   some systems may have changed the meaning. Note that initially each
   sentence is presented twice. The upper (grey) box is fixed, but the
   lower (white) is editable.

2. Edit each of the white text boxes so that the sentence is grammatically
   correct and sounds natural. If there are multiple ways of achieving these
   goals, choose the one that results in the least changes. Note that the
   changes you have made will be highlighted, to make it easier for you to see
   and remember what you changed.

3. For each system, choose Grammaticality rating and Fluency rating from their
   respective scroll-down menus. Leave the Meaning Preservation rating for
   now.

4. Press the "Save" button in the bottom left. The black text field will now
   display a *reference* containing the intended meaning of the sentences.
   This has been written by a human annotator with access to more context, and
   for the purposes of this task you can assume that this interpretation is
   correct. Note that this version is *not* meant to sound natural, just to be
   grammatically correct and convey the intended meaning.

5. Confirm that your corrected sentences mean the same thing as the reference
   sentence. If not, edit them so that they are still grammatically correct,
   sound natural, and mean the same thing as the reference. When you have
   finished a sentence, assign a Meaning Preservation rating. If you did not
   make any changes, the value should be "Identical". Otherwise, assign a
   different value depending on how different the meaning was from what you
   intended.

6. Press the "Confirm" (where the "Save" button used to be). Now your
   annotations for this example have been saved.

7. Either press `>>>` to move forward to the next example, or "Quit" to
   finish. Note that `<<<` (go to the previous example), `>>>` and "Quit" will
   all discard any changes made. Only pressing "Save" followed by "Confirm"
   will save any changes.

## Notes

* The different ratings all have the possible value "Other". This is mainly
  meant for cases when GEC systems have malfunctioned, or when the input data
  is not a proper sentence. For instance, if the output is a single number, a
  single word repeated multiple times, or obviously erroneous in some other
  way, you can assign "Other". Typically this applies to all categories at the
  same time: Grammicality, Fluency and Meaning Preservation.

