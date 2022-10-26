#Annotation guidelines

##Grammaticality

Based on Heilman et al. (2014), as appearing in Yoshimura et al. (2020).
The definitions below are from Heilman et al. (2014, p. 175). Examples are
adapted from SweLL.

Note that grammaticallity is defined with respect to the system output only,
even if this diverges from the reference. For instance, even if the reference
sentence is "I have a book", a sentence like "I have the book" would be
considered perfect with respect to grammaticality, because it is correct given
a slightly different interpretation. On the other hand, "I has a book" has a
lower degree of grammaticality, because there is *no* interpretation where it
would be correct. For the property of
[meaning preservation](#meaning-preservation), the situation is reversed and
the second sentence would be scored higher.

##Perfect

*The sentence is native-sounding. It has no grammatical errors, but may
contain very minor typographical and/or collocation errors.*

We do not take the "native-sounding" requirement literally, and the second
part of the definition explicitly allows collocation errors, which presumably
make the sentence less native-sounding.

Example: **jag tror att det finns bra möjligheter att uttrycka sig genom kläder i Sverige eftersom man nästan kan ha på sig vad man vill .**

This sentence contains a word choice error (tycker/tror) which changes the
interpretation slightly, and the position of "nästan" may be a bit unusual but
is acceptable. It is not properly capitalized, but following Heilman et al.
this is also accepted.

##Comprehensible

*The sentence may contain one or more minor grammatical errors, including
subject-verb agreement, determiner, and minor preposition errors that do not
make the meaning unclear.*

Example: **Jag tror att det finns bra möjligheter att uttrycker sig genom kläder i Sverige eftersom man nästan kan ha på sig vad man vill .**

There is a clear verb form error (att uttrycker), but the understanding of the
sentence is not affected.

##Somewhat comprehensible

*The sentence may contain one or more serious grammatical errors, including
missing subject, verb, object, etc., verb tense errors, and serious
preposition errors. Due to these errors, the sentence may have multiple
plausible interpretations.*

Example: **Jag tror finns bra möjligheter att uttrycker sig av kläder i Sverige eftersom nästan kan ha på sig vad man vill .**

There are multiple errors, including a preposition error (*av* rather than
*genom*) that makes it difficult to know whether it is difficult to express
one's opinions about clothing, or to express oneself through one's clothing.

##Incomprehensible

*The sentence contains so many errors that it would be difficult to
correct.*

We take this to mean that it would be difficult to correct because it
is difficult to comprehend.

Example: **Jag tror möjlig uttrycker kläderna i Sverige man då nästan kan vill ha det .**


#Fluency

Based on Lau et al. (2015). No definitions are given except the labels, so we
rely heavily on native speaker judgement.

Note that fluency, like grammaticality, is defined with respect to the system
output only. The meaning may be completely implausible or different from the
reference, but if the sentence could have been produced by a native speaker in
some other context, we consider it to sound natural.

Low grammaticallity always implies low fluency, but the opposite is not true.
A sentence that is technically grammatical could still sound unnatural, if a
native speaker would be unlikely to produce it.

##Extremely natural

Example: **Jag tror att du förstår mina problem även om jag inte är kvar i
kursen .**

This does not mean the same thing as the SweLL reference at all, but sounds
native-like in a different context. Thus it has high grammaticality and
fluency, but does not preserve meaning.

##Somewhat natural

Example: **Kan lycka mätas i förhållande till landets ekonomiska eller ens
egen framgång ?**

This is grammatical and in fact identical to the SweLL reference, but a bit
awkward. There are two interpretations (is one's own success economical, or
just general success?) and the disjunction would probably have been expressed
by a native speaker to clarify this: **landets eller ens egen ekonomiska
framgång** or **landets ekonomiska framgång eller ens egen framgång**.

##Somewhat unnatural

Example: **Om du håller med min förslag kan vi köpa den imorgon .**

This is ungrammatical (gender agreement: min förslag), and normally the
preposition "om" would be used before that NP. But since the construction
"håller med [person]" (without "om") exists with a slightly different meaning
(agrees with [person]), the end result is easy to interpret. Overall this
results in a clearly non-native sentence with two grammatical errors, but of a
kind one would barely react to if spoken by someone known to be a non-native
speaker.

Example: **Jag frågade min kusin från Tyskland om det , och min kusin från
Tyskland avtäckte att det inte går .**

This is grammatical, but the full NP (min kusin från Tyskland) is repeated
where a native speaker would most likely use an abbreviated reference like a
pronoun. In addition, there is a word choice error (avtäckte) is interpretable
only with some effort.

##Extremely unnatural

Example: **Jag är mår bra.**

Although there is only a single error, the combination of two present-tense
verbs sounds rather unnatural, and probably belongs between the "somewhat
unnatural" and "extremely unnatural" categories.

Example: **Jag tror att du förstår mina problem även borta mig från den kursen .**

This has lower fluency than the previous example. The use of "borta" as a verb
(instead of "ta bort"), several words are missing around "även", and an extra
determiner ("den") is inserted at the end.

Example: **Om du är håller med min förslag vi kan köpa den imorgon .**

This is similar to the example under "somewhat unnatural" above, except the
 "är" + present tense combination and a word order error (vi kan) later in
the sentence.


#Meaning preservation

We use the scale from Yoshimura et al. (2020). They cite Xu et al (2016), but
as far as I can see they only mention a "5-point scale" without any further
details.

Note that meaning preservation is with respect to the *reference*. This means
that a GEC system which does not perform any edits at all can also have a low
meaning preservation score, if the original sentence has a literal
interpretation different from the reference. For instance, consider the
following case:

Original: **My grandfather dyed before I was birthed**

Human reference: **My grandfather died before I was born**

System output: **My grandfather dyed before I was born**

During annotation we assume that the human reference contains the correct
interpretation of each sentence (the SweLL annotators have access to a wider
context). Therefore, the *intended* meaning of the original sentence has not
been "preserved" (or rather, inferred) by the GEC system, and would probably
be classified as "moderate differences" or even "substantially different"
because the semantics of the whole sentence change radically.

The examples given below are relative to the following example.

Reference: **Jag tror att du förstår mitt problem så att du även kan ta bort mig från kursen .**

##Identical

Example: **Jag tror att du förstår mitt problem och kan därför avregistrera mig från kursen .**

Note that there are several surface-level differences, like the use of
"avregistrera" rather than "ta bort" (synonymous in this context), and the
different way of connecting the two main parts of the sentence ("så att du
även kan" vs "och kan därför").

##Minor differences

Example: **Jag tror att du förstår mitt problem och kan därför ta bort mig
från en kurs .**

The final noun (kurs) was changed from definite to indefinite. Differences in
e.g. definiteness or number will typically be classified as "minor
differences".

##Moderate differences

Example: **Jag vet att du förstår mitt problem och kan därför ta in mig i
kursen  .**

Two of the verbs have been changed to semantically related but different ones
(tror/vet, ta in/ta bort).

##Substantially different

Example: **Jag tror att du förstår mina problem även om jag inte är kvar i kursen .**

The meaning of the second part is very different from the reference. This
example is around the border between "moderate differences" and "substantially
different". Anything more different from the reference than this should be
annotated as "substantially different". In theory this is a large category of
possible sentences, but in practice it is rather rare for GEC systems to
corrupt sentence semantics to this degree.

