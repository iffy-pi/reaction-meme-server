import json
import sys
import os

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh import index
from whoosh.qparser import QueryParser, OrGroup, MultifieldParser
from contextlib import contextmanager


@contextmanager
def test():
    file = None
    try:
       yield 1
    finally:
        print('Closing file')




def main():
    # create our schema, fields in the document we are searching or storing per search
    schema = Schema(fileID=STORED,
                    name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
                    tags=KEYWORD(lowercase=True, scorable=True, commas=True, analyzer=StemmingAnalyzer()))

    # create our index, maps the searchable fields to actual documents, in this case our json element IDs
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")

    # if index.exists_in("indexdir"):
    #     ix = index.open_dir("indexdir")
    # else:
    ix = index.create_in("indexdir", schema)

    with open('preDB.json', 'r') as file:
        db = json.load(file)

    # Add documents to the schema
    writer = ix.writer()

    for elem in db['elements'].values():
        # print('Adding element:')
        # print(elem)
        writer.add_document(fileID=elem['id'], name=elem['name'], tags=','.join(elem['tags']))

    writer.commit()

    qp = MultifieldParser(["tags", "name"], schema=ix.schema, group=OrGroup)
    q = qp.parse(u"human torture")

    with ix.searcher() as s:
        results = s.search(q)
        for r in results:
            print(r['fileID'])



    return 0



if __name__ == "__main__":
    sys.exit(main())