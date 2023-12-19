from contextlib import contextmanager

from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, STORED
from whoosh.qparser import OrGroup, MultifieldParser
from whoosh.filedb.filestore import RamStorage

from apiutils.MemeManagement.MemeLibraryItem import MemeLibraryItem


class MemeLibrarySearcher:
    """
    Implements indexing and searching of memes for MemeLibrary
    """
    # Note: This has been configured to use a specific set of field names: memeID, name, tags
    # If the fields have been changed be sure to change all places marked with the comment:
    # KEYFIELDS_RELEVANT_HERE
    def __init__(self):
        # we create our scheme here
        # Each keyword argument is a field name in the schema
        # KEYFIELDS_RELEVANT_HERE
        self.__schema = Schema(
            memeID=STORED,
            memeURL=STORED,
            name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            tags=KEYWORD(lowercase=True, scorable=True, commas=True, analyzer=StemmingAnalyzer())
        )

        # Field parser for the query, the fieldnames list should match the field names above
        # Designed to search in both names and tag field, using an or-ing of results
        # KEYFIELDS_RELEVANT_HERE
        self.__queryParser =  MultifieldParser(
                ["name", "tags"],
                schema=self.__schema,
                group=OrGroup
        )

        # other initi
        self.__index = None
        self.__indexStorage = RamStorage()
        self.__indexLock = None

    # TODO: Is our mutex/semaphore lock stuff configured correctly, ELEC 377 review
    # TODO: Do DB locks in db class
    def __isIndexLocked(self):
        return self.__indexLock

    def __getIndexLock(self):
        # wait till index unlocks
        while self.__isIndexLocked():
            pass

        self.__indexLock = True

    def __releaseIndexLock(self):
        self.__indexLock = False

    def __addMemeToWriter(self, indexWriter, meme:MemeLibraryItem):
        # KEYFIELDS_RELEVANT_HERE
        indexWriter.add_document(memeID=meme.getID(),
                                 name=meme.getName(),
                                 tags=','.join(meme.getTags()),
                                 memeURL=meme.getURL()
                                 )

    def hasIndex(self):
        return self.__index is not None

    def indexMemeList(self, memes:list[MemeLibraryItem]):
        """
        Indexes all the memes in the library, if index already exists, it is re-indexed
        :return:
        """
        self.__getIndexLock()

        # Creates a fresh index
        self.__index = self.__indexStorage.create_index(self.__schema)

        # open the writer to add documents to the index
        writer = self.__index.writer()
        for meme in memes:
            self.__addMemeToWriter(writer, meme)
        writer.commit()

        # release the lock
        self.__releaseIndexLock()

    def indexMeme(self, meme:MemeLibraryItem):
        self.__getIndexLock()
        writer = self.__index.writer()
        self.__addMemeToWriter(writer, meme)
        self.__releaseIndexLock()

    @contextmanager
    def getSearcher(self):
        if self.__index is None:
            raise Exception('Database has not been indexed')

        self.__getIndexLock()
        searcher = self.__index.searcher()
        try:
            yield searcher
        finally:
            searcher.close()
            self.__releaseIndexLock()

    def __hitToSearchResult(self, hit):
        # KEYFIELDS_RELEVANT_HERE
        return {"memeID": hit["memeID"],
                  "name": hit["name"],
                  "memeURL": hit["memeURL"],
                  }

    def __parseResults(self, results):
        return [ self.__hitToSearchResult(hit) for hit in results ]

    def search(self, query:str, itemsPerPage, pageNo):
        q = self.__queryParser.parse(query)
        with self.getSearcher() as s:
            results = s.search_page(q, pageNo, pagelen=itemsPerPage)
            return self.__parseResults(results)

    def getSearchResultAttr(self, result, memeID:bool=False, name:bool=False, memeURL:bool=False):
        """
        Retrieves a stored property from the search results.
        Simply set the property param of the property you would like to retrieve to true
        """
        # KEYFIELDS_RELEVANT_HERE
        if memeID:
            return result["memeID"]
        if name:
            return result["name"]
        if memeURL:
            return result["memeURL"]