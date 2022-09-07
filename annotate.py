#-*-coding:utf8-*-

import stanza
import classla
from collections import defaultdict
from googletrans import Translator
translator = Translator()
import string
import re
##stanza.download('hr')
##stanza.download('sr')
#stanza.download('cs')
#stanza.download('pl')
#stanza.download('ru')
#stanza.download('cu')
langs = ["pl", "ru", "cs", "bcms", "cu"]
class Input2Conllu():
    def __init__(self, inputfile, annotated_output):
        self.inputfile = inputfile
        self.annotated_output = annotated_output
        self.inputdict = self.input2dict()
        self.trlangs = ["pl", "ru", "cs", "sr"]

    def xstr(self, s):
        if s is None:
            return "-"
        return str(s)

    #def textid(self, mylang, counter, version):
    def textid(self, mylang, myversion, counter):
        if mylang in langs:
            id = mylang+str(myversion).zfill(2)+str(counter).zfill(5)
            #id = mylang+str(counter).zfill(5)
            return id
        else:
            print("the language should be one of the following:" + " ".join(langs))
            exit()

    #def tokenid(self, mylang, counter, version):
    def tokenid(self, mylang, myversion, counter):
        if mylang in langs:
            id = mylang+str(myversion).zfill(2)+str(counter).zfill(7)
           # id = mylang+str(counter).zfill(7)
            return id
        else:
            print("the language should be one of the following:" + " ".join(langs))
            exit()

    def input2dict(self):
        d = defaultdict(list)
        for line in open(self.inputfile).readlines()[1:]:
            line = line.rstrip("\n")
            linesp = line.split("\t")
            #version = linesp[8]
            d[linesp[0]] += [linesp[1:]]
        for key in d:
            c = 0
            #version="test"
            for v in d[key]:
                version = v[8]

                #print(v)
                c+=1
                id = self.textid(key, version, c)
                v.append(id)
        return d

    def translate(self, mylemma, mykey, upos):
        ## sometimes google blocks this because there are too many requests
        punc = string.punctuation
        if mylemma in punc:
            return mylemma
        else:
            if mykey in self.trlangs:
                translation = translator.translate(mylemma, src=mykey)
                #print(mykey, translation.origin, ' -> ', translation.text)
                if upos == "PROPN":
                    return translation.text
                else:
                    return translation.text.lower()
            else:
                return "-"

    def getGender(self, myfeat, mygender):
        if myfeat[myfeat.index("=")+1:] == "Masc":
            mygender+="M"
        elif myfeat[myfeat.index("=")+1:] == "Fem":
            mygender+="F"
        return mygender
    def getNumber(self,myfeat, mynumber):
        if myfeat[myfeat.index("=")+1:] == "Sing":
            mynumber+="SG"
        elif myfeat[myfeat.index("=")+1:] == "Plur":
            mynumber+="PL"
        return mynumber
    def getDefinite(self,myfeat, mydefinite):
        if myfeat[myfeat.index("=")+1:] == "Def":
            mydefinite+="DEF"
        elif myfeat[myfeat.index("=")+1:] == "Ind":
            mydefinite+="INDF"
        return mydefinite
    def getAspect(self, myfeat, myaspect):
        if myfeat[myfeat.index("=")+1:] == "Perf":
            myaspect+="PFV"
        elif myfeat[myfeat.index("=")+1:] == "Impf":
            myaspect+="IPFV"
        return myaspect
    def getModus(self, myfeat, mymodus):
        if myfeat[myfeat.index("=")+1:] == "Ind":
            mymodus +="IND"
        elif myfeat[myfeat.index("=")+1:] == "Imp":
            mymodus +="IMP"
        elif myfeat[myfeat.index("=")+1:] == "Cnd":
            mymodus += "COND"
        return mymodus
    def getTempus(self, myfeat, mytempus):
        if myfeat[myfeat.index("=")+1:] == "Fut":
            mytempus+= "FUT"
        elif myfeat[myfeat.index("=")+1:] == "Imp":
            mytempus+= "IPFV"
        elif myfeat[myfeat.index("=")+1:] == "Past":
            mytempus+="PST"
        elif myfeat[myfeat.index("=")+1:] == "Pres":
            mytempus+="PRS"
        return mytempus

    def addGloss(self, myfeat, myupos, myxpos, mydeprel):
        ## - Nomen/Adjektive: Kasus, Genus, Numerus, ggf. Def.
        gloss = []
        #print("\n\n"+myfeat+"\n\n")
        if myupos == "NOUN" or myupos == "ADJ":
            if myfeat is not None:
                myfeat = myfeat.split("|")
                #Case=Gen|Definite=Def|Degree=Pos|Gender=Masc|Number=Plur
                ## TODO: check if categories should be omitted (ex. both Fem,Masc) in Altkirchenslavisch
                case = ""
                number = ""
                gender = ""
                definite = ""
                for feat in myfeat:
                    if feat.startswith("Case"):
                        case+=feat[feat.index("=")+1:].upper()
                    if feat.startswith("Number"):
                        number = self.getNumber(feat, number)
                    if feat.startswith("Gender"):
                        gender = self.getGender(feat, gender)
                    if feat.startswith("Definite"):
                        definite = self.getDefinite(feat, definite)
                gloss.append([case, number, gender, definite])
                str_list = list(filter(None, gloss[0]))
                return (".".join(str_list))
            else:
                return "-"
        elif myupos == "VERB" or myupos == "AUX":
            if myfeat is not None:
                myfeat = myfeat.split("|")
                # - Verben: Aspekt, Modus, Tempus, Person, Numerus, ggf. Refl.
                #Aspect=Perf|Gender=Masc|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Mid
                #Mood=Ind|Number=Sing|Person=3|Polarity=Pos|Tense=Pres|VerbForm=Fin|Voice=Act
                aspect = ""
                modus = ""
                tempus = ""
                person = ""
                number = ""
                gender = ""
                for feat in myfeat:
                    if feat.startswith("Aspect"):
                        aspect = self.getAspect(feat, aspect)
                    if feat.startswith("Mood"):
                        modus = self.getModus(feat, modus)
                    if feat.startswith("Tense"):#Fut	Imp	Past	Pqp	Pres
                        tempus = self.getTempus(feat, tempus)
                    if feat.startswith("Person"):
                        person+=feat[feat.index("=")+1:]
                    if feat.startswith("Number"):
                        number = self.getNumber(feat, number)
                    if feat.startswith("Gender"):
                        gender = self.getGender(feat, gender)
                #elif
                ## Plusquamperfect
                #elif feat[feat.index("=")+1:] == "Pqp":
                # tempus+="PST"
                gloss.append([aspect, modus, tempus, person, number, gender])
                str_list = list(filter(None, gloss[0]))
                return (".".join(str_list))
            else:
                return "-"

        elif myupos == "PART" and myfeat=="Polarity=Neg":
            return "NEG" ## negation particles
        elif myxpos == "Qq":
            return "Q" ## question particle
        elif myupos == "SCONJ" and mydeprel == "mark":
            return "COMP"  #complementiser

    ## for replacing punctuation marks of direct speech, which cause trouble in the tokenisation
    def replace_sonderzeichen(self, sentence):
        return sentence.replace('"', "-")\
            .replace("»", "-")\
            .replace("«", "-")\
            .replace("„", "-")\
            .replace("“", "-")\

    def underline_content_in_eckigen_klammern(self, sentence):
        ## this is not always accurate
        substring = re.findall('\[.+?\]', sentence)
        for s in substring:
            replaced = s.replace("[", "xxx") \
                .replace("]", "") \
                .replace(" ", " xxx")
            sentence = sentence.replace(s, replaced)
        return sentence

    def get_underlined_ids(self,my_doc_replaced, myexample_id, dict_of_underlined_ids):
        t_counter = 0
        for i, sentence in enumerate(my_doc_replaced.sentences):
            for token in sentence.words:
                t_counter +=1
                if token.text.startswith("xxx"):
                    dict_of_underlined_ids[myexample_id] +=[t_counter]
        return dict_of_underlined_ids

    def dict2conllu(self):
        conllu_file = open(self.annotated_output, "w")
        conllu_file.write("\t".join(["ID","FORM","LEMMA","UPOS","XPOS", "FEATS","HEAD","DEPREL", "MISC","ENGLISH","GLOSS", "GLOSSKORR", "OMIT_ANNOTATIONS", "TOKENID", "EXAMPLEID", "_CAT","_EDITOR"])+"\n")
        for key in sorted(self.inputdict):
            c_token = 0
            ## Set the Serbian parser if language = bcms
            lang = ""
            if key == "bcms":
                lang += "sr"
                nlp = classla.Pipeline(lang)
            else:
                lang += key
                nlp = stanza.Pipeline(lang)
            # sort dict according to alignment id (k[5])
            # TODO: check this sorting again
            for example in sorted(self.inputdict[key],key=lambda k: (k[5])):
                #print (example)
                version = example[8]
                # LANGCODE	EXAMPLE	SOURCE	REFERENCE	REFERENCE_PAGE	CAT	GROUPID	EDITOR	COMMENT	VERSION	COMMENT_INTERN
                example_text = self.replace_sonderzeichen(example[0])
                category = example[4]
                editor = example[6]
                example_id = example[-1]
                dict_underlined_ids = defaultdict(list)

                if "[" in example_text:
                    # nlp the example without klammern
                    example_text_stripped_klammer = example_text.replace("[", "").replace("]", "")
                    doc = nlp(example_text_stripped_klammer)
                    ###
                    underlined_content = self.underline_content_in_eckigen_klammern(example_text)
                    ## nlp the example with underscores for each word in klammer for getting the indexes of that word
                    doc_replaced = nlp(underlined_content)
                    ## get ids of underlined words
                    dict_underlined_ids = self.get_underlined_ids(doc_replaced, example_id, dict_underlined_ids)
                else:
                    doc = nlp(example_text)
                sec_t_counter = 0
                for sentence in doc.sentences:
                    for word in sentence.words:
                        sec_t_counter +=1
                        c_token+=1
                        tokenid = self.tokenid(key, version, c_token)
                        omit_annotations = ""
                        if sec_t_counter in dict_underlined_ids[example_id]:
                        #if int(word.id) in dict_underlined_ids[example_id]:
                            omit_annotations += "_omit_annotations_"
                        else:
                            omit_annotations += ""
                        conllu_file.write("\t".join([self.xstr(word.id),
                                                    self.xstr(word.text),
                                                    self.xstr(word.lemma),
                                                    self.xstr(word.upos),
                                                    self.xstr(word.xpos),
                                                    self.xstr(word.feats),
                                                    self.xstr(word.head),
                                                    self.xstr(word.deprel),
                                                    self.xstr(word.misc),
                                                    ## add translation
                                                    self.translate(self.xstr(word.lemma), lang, self.xstr(word.upos)),
                                                    ## add Leipzig Glosses
                                                    self.xstr(self.addGloss(word.feats, word.upos, word.xpos, word.deprel)),
                                                    ## add empty column for corrections
                                                    "",
                                                    ## omit annotations
                                                    omit_annotations,
                                                    ## add token id
                                                    tokenid,
                                                    ## add example id
                                                    example_id,
                                                    ## add language,
                                                    #key,
                                                    ## add category
                                                    category,
                                                    ## add verantwortlich
                                                    editor
                                                     ])+"\n")



if __name__ == "__main__":
    output = Input2Conllu("tables/data_input/input.tsv", "tables/data_output/tokens.tsv")
    x = output.dict2conllu()



