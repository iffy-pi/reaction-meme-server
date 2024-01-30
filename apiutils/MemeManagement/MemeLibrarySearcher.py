from contextlib import contextmanager

from whoosh import query
from whoosh.analysis import StemmingAnalyzer
from whoosh.fields import Schema, TEXT, KEYWORD, STORED, NUMERIC
from whoosh.qparser import OrGroup, MultifieldParser
from whoosh.filedb.filestore import RamStorage
from whoosh.searching import Searcher, Hit

from apiutils.MemeManagement.MemeContainer import MemeContainer
from apiutils.MemeManagement.MemeMediaType import intToMemeMediaType, MemeMediaType, memeMediaTypeToInt


class MemeLibrarySearcherException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class MemeSearchHit:
    """
    A container class used to store a hit in the search.
    A hit meaning a matching item in the index
    """
    def __init__(self, hit: Hit):
        # SCHEMA_FIELDS_RELEVANT_HERE
        # Hit class should have properties for all the storable fields
        self.memeID = hit['memeID']
        self.name = hit['name']
        self.mediaType = intToMemeMediaType(hit['mediaType'],)
        self.memeURL = hit['memeURL']

class MemeLibrarySearcher:
    """
    Implements indexing and searching of memes for MemeLibrary
    """
    # Note: This has been configured to use a specific set of field names: memeID, name, tags
    # If the fields have been changed be sure to change all places marked with the comment:
    # SCHEMA_FIELDS_RELEVANT_HERE
    def __init__(self):
        # we create our scheme here
        # Each keyword argument is a field name in the schema
        # SCHEMA_FIELDS_RELEVANT_HERE
        self.__schema = Schema(
            memeID=STORED,
            memeURL=STORED,
            name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
            mediaType=NUMERIC(stored=True),
            tags=KEYWORD(lowercase=True, scorable=True, commas=True, analyzer=StemmingAnalyzer())
        )

        # Field parser for the query, the fieldnames list should match the field names above
        # Designed to search in both names and tag field, using an or-ing of results
        # SCHEMA_FIELDS_RELEVANT_HERE
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
    def __isIndexLocked(self):
        return self.__indexLock

    def __getIndexLock(self):
        # wait till index unlocks
        while self.__isIndexLocked():
            pass

        self.__indexLock = True

    def __releaseIndexLock(self):
        self.__indexLock = False

    def __addMemeToWriter(self, indexWriter, meme:MemeContainer):
        # SCHEMA_FIELDS_RELEVANT_HERE
        indexWriter.add_document(memeID=meme.getID(),
                                 name=meme.getName(),
                                 tags=','.join(meme.getTags()),
                                 memeURL=meme.getURL(),
                                 mediaType=meme.getMediaTypeInt()
                                 )

    def hasIndex(self) -> bool:
        return self.__index is not None

    def indexMemeList(self, memes:list[MemeContainer]):
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

    def indexMeme(self, meme:MemeContainer):
        self.__getIndexLock()
        writer = self.__index.writer()
        self.__addMemeToWriter(writer, meme)
        self.__releaseIndexLock()

    @contextmanager
    def getSearcher(self) -> Searcher:
        if self.__index is None:
            raise MemeLibrarySearcherException('Database has not been indexed')

        self.__getIndexLock()
        searcher = self.__index.searcher()
        try:
            yield searcher
        finally:
            searcher.close()
            self.__releaseIndexLock()


    def search(self, queryStr:str, itemsPerPage, pageNo, onlyMediaType: MemeMediaType=None, excludeMediaType: MemeMediaType = None) -> list[MemeSearchHit]:
        q = self.__queryParser.parse(queryStr)
        filterTypeQuery = None
        excludeTypeQuery = None

        with self.getSearcher() as s:
            # SCHEMA_FIELDS_RELEVANT_HERE
            if onlyMediaType is not None:
                filterTypeQuery = query.Term("mediaType", str(memeMediaTypeToInt(onlyMediaType)))

            if excludeMediaType is not None:
                excludeTypeQuery = query.Term("mediaType", str(memeMediaTypeToInt(excludeMediaType)))

            results = s.search_page(q, pageNo, pagelen=itemsPerPage, filter=filterTypeQuery, mask=excludeTypeQuery)
            resultCount = results.scored_length()
            startOffset = (pageNo - 1) * itemsPerPage

            if startOffset < resultCount:
                return [ MemeSearchHit(hit) for hit in results ]

            return []