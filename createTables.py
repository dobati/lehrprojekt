from annotate import *
inputfile = "tables/data_input/input.tsv"
annotated_output = "tables/data_output/tokens.tsv"
category = open("tables/data_output/category.tsv", "w")
slavexample = open("tables/data_output/slavexample.tsv", "w")

category.write("\t".join(["CAT","EXAMPLEID"])+"\n")
slavexample.write("\t".join(["SOURCE","REFERENCE", "REFERENCE_PAGE","GROUPID","_EDITOR","COMMENT","VERSION", "_COMMENT_INTERN" ,"EXAMPLEID"])+"\n")

tokens_table = Input2Conllu(inputfile, annotated_output)

## create tokens table (in conllu format)
#x = tokens_table.dict2conllu()

def createCategoryTable(myexample, myfile):
    ## category has the index 3
    cat_index = myexample[4]
    if len(cat_index)>0:
        for category in cat_index.split(", "):
            exampleid = myexample[-1]
            myfile.write("\t".join([category, exampleid])+"\n")


def createSlavExampleTable(myexample, myfile):
    # 9 column have to be specified: example, source, ref, cat, alignment, editor, comment, version, example_id
    source = myexample[1]
    reference = myexample[2]
    reference_page = myexample[3]
    groupid = str(myexample[5])
    editor = myexample[6]
    comment = myexample[7]
    version = myexample[8]
    comment_intern = myexample[9]
    exampleid = myexample[-1]
    myfile.write("\t".join([source, reference, reference_page, groupid, editor, comment, version, comment_intern, exampleid])+"\n")
    return "pass"

for key in sorted(tokens_table.inputdict):
    #print(key, tokens_table.inputdict[key])
    # sort according to alignment id
    ## sorting on groupid failed to implement
    for example in sorted(tokens_table.inputdict[key],key=lambda k: k[5]):
        if len(example)==11:
            # 11 column have to be specified: example, source, ref, red_page, cat, alignment, editor, comment, version, comment_intern, example_id
            createCategoryTable(example, category)
            createSlavExampleTable(example, slavexample)
        else:
            print("there have to be 9 columns in the data list:\nexample, source, ref, cat, alignment, editor, comment, version, example_id")
