from comp62521.statistics import average
import itertools
import numpy as np
from xml.sax import handler, make_parser, SAXException
from flask import Markup
from difflib import SequenceMatcher

PublicationType = [
    "Conference Paper", "Journal", "Book", "Book Chapter"]

class Publication:
    CONFERENCE_PAPER = 0
    JOURNAL = 1
    BOOK = 2
    BOOK_CHAPTER = 3

    def __init__(self, pub_type, title, year, authors):
        self.pub_type = pub_type
        self.title = title
        if year:
            self.year = int(year)
        else:
            self.year = -1
        self.authors = authors
        
    def __str__(self):
        return "{0}({1}): {2}".format (self.title, self.year, ", ".join( [str(a) for a in self.authors ] ) )
                
#
#   Author
#   
#   Modified to split the provided name into a first and last
#
class Author:

    #static varible
    href = "<a href='/author_stats?author_search="

    def __init__(self, name):
        self.name = name
        
        #"andy paul stob" => "andy+paul+stob"
        self.authorSearch = "+".join(name.split(" "))        
        
        self.HTMLName = Markup(self.href + self.authorSearch + "'>" + self.name + "</a>")
        
                             
        authorName = self.name.rsplit(None,1)
        if len(authorName) == 1:
            self.surname = self.name
            self.firstName = ""
        else:    
            self.surname = authorName[1].strip()
            self.firstName = authorName[0].strip()
            
        self.HTMLFirstName = Markup(self.href + self.authorSearch + "'>" + self.firstName + "</a>")
        self.HTMLSurname = Markup(self.href + self.authorSearch + "'>" + self.surname + "</a>")               
            

                                
    @staticmethod  
    def MakeFullName(name):
        return Markup( "<a href='/author_stats?author_search=" + "+".join(name.split(" ")) + "'>" + name + "</a>")
    

class Stat:
    STR = ["Mean", "Median", "Mode"]
    FUNC = [average.mean, average.median, average.mode]
    MEAN = 0
    MEDIAN = 1
    MODE = 2

class Database:
    def read(self, filename):
        self.publications = []
        self.authors = []
        self.author_idx = {}
        self.min_year = None
        self.max_year = None

        handler = DocumentHandler(self)
        parser = make_parser()
        parser.setContentHandler(handler)
        infile = open(filename, "r")
        valid = True
        try:
            parser.parse(infile)
        except SAXException as e:
            valid = False
            print "Error reading file (" + e.getMessage() + ")"
        infile.close()

        for p in self.publications:
            if self.min_year == None or p.year < self.min_year:
                self.min_year = p.year
            if self.max_year == None or p.year > self.max_year:
                self.max_year = p.year

        return valid

    def get_all_authors(self):
        return self.author_idx.keys()
        
    def get_all_authors_sorted(self):
        retVal = []
        for x in range(0,len(self.authors)):
            retVal.append((x,self.authors[x].name))
            
        retVal.sort(
                        key=lambda tup: 
                            (
                                self.authors[tup[0]].surname
                                , self.authors[tup[0]].firstName
                            )
                    )
        
        return retVal

    def get_author_index(self, pAuthorName):
	for x in range(0, len(self.authors)):
	    if self.authors[x].name == pAuthorName:
		return int(x)    
        
    
    #
    #    Get Publication Data
    #
    def getPublication(self, pIndex):
        return "{0}({1}) - {2}".format(
            self.publications[pIndex].title, 
            self.publications[pIndex].year
            , [[self.authors[a].name] for a in self.publications[pIndex].authors])            
            

    #
    #   get_coauthor_data
    #
    def get_coauthor_data(self, start_year, end_year, pub_type):
        coauthors = {}
        for p in self.publications:
            if ((start_year == None or p.year >= start_year) and
                (end_year == None or p.year <= end_year) and
                (pub_type == 4 or pub_type == p.pub_type)):
                for a in p.authors:
                    for a2 in p.authors:
                        if a != a2:
                            try:
                                coauthors[a].add(a2)
                            except KeyError:
                                coauthors[a] = set([a2])
                                
        #modified to replace authorname with author surname and first name
        def display(db, coauthors, author_id):
            return "%s (%d)" % (db.authors[author_id].HTMLName, len(coauthors[author_id]))
            
        #modified to change authorname to firstname / lastname
        header = ("Author First Name", "Author Surname", "Paper Count", "Co-Authors")
        data = []
        for a in coauthors:
            data.append([ self.authors[a].HTMLFirstName, self.authors[a].HTMLSurname, len(coauthors[a]),
                Markup(", ".join([display(self, coauthors, ca) for ca in coauthors[a] ])) ])

        return (header, data)

    def get_average_authors_per_publication(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ func(auth_per_pub[i]) for i in np.arange(4) ] + [ func(list(itertools.chain(*auth_per_pub))) ]
        return (header, data)

    def get_average_publications_per_author(self, av):
        header = ("Conference Paper", "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))

        for p in self.publications:
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(pub_per_auth[:, i]) for i in np.arange(4) ] + [ func(pub_per_auth.sum(axis=1)) ]
        return (header, data)

    def get_average_publications_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        ystats = np.zeros((int(self.max_year) - int(self.min_year) + 1, 4))

        for p in self.publications:
            ystats[p.year - self.min_year][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(4) ] + [ func(ystats.sum(axis=1)) ]
        return (header, data)

    def get_average_authors_in_a_year(self, av):
        header = ("Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        yauth = [ [set(), set(), set(), set(), set()] for _ in range(int(self.min_year), int(self.max_year) + 1) ]

        for p in self.publications:
            for a in p.authors:
                yauth[p.year - self.min_year][p.pub_type].add(a)
                yauth[p.year - self.min_year][4].add(a)

        ystats = np.array([ [ len(S) for S in y ] for y in yauth ])

        func = Stat.FUNC[av]

        data = [ func(ystats[:, i]) for i in np.arange(5) ]
        return (header, data)

    def get_publication_summary_average(self, av):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "All Publications")

        pub_per_auth = np.zeros((len(self.authors), 4))
        auth_per_pub = [[], [], [], []]

        for p in self.publications:
            auth_per_pub[p.pub_type].append(len(p.authors))
            for a in p.authors:
                pub_per_auth[a, p.pub_type] += 1

        name = Stat.STR[av]
        func = Stat.FUNC[av]

        data = [
            [name + " authors per publication"]
                + [ func(auth_per_pub[i]) for i in np.arange(4) ]
                + [ func(list(itertools.chain(*auth_per_pub))) ],
            [name + " publications per author"]
                + [ func(pub_per_auth[:, i]) for i in np.arange(4) ]
                + [ func(pub_per_auth.sum(axis=1)) ] ]
        return (header, data)

    def get_publication_summary(self):
        header = ("Details", "Conference Paper",
            "Journal", "Book", "Book Chapter", "Total")

        plist = [0, 0, 0, 0]
        alist = [set(), set(), set(), set()]

        for p in self.publications:
            plist[p.pub_type] += 1
            for a in p.authors:
                alist[p.pub_type].add(a)
        # create union of all authors
        ua = alist[0] | alist[1] | alist[2] | alist[3]

        data = [
            ["Number of publications"] + plist + [sum(plist)],
            ["Number of authors"] + [ len(a) for a in alist ] + [len(ua)] ]
        return (header, data)

    def get_average_authors_per_publication_by_author(self, av):
        header = ("Author", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "All publications")

        astats = [ [[], [], [], []] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [self.authors[i].name]
            + [ func(L) for L in astats[i] ]
            + [ func(list(itertools.chain(*astats[i]))) ]
            for i in range(len(astats)) ]
        return (header, data)

    #
    #   get_publications_by_author
    #
    def get_publications_by_author(self):
        #modified to add firstname, last name columns
        header = ("Author First Name", "Author Surname", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        astats = [ [0, 0, 0, 0] for _ in range(len(self.authors)) ]
        for p in self.publications:
            for a in p.authors:
                astats[a][p.pub_type] += 1

        #replace author.name with surname and firstname
        data = [ [self.authors[i].HTMLFirstName] + [self.authors[i].HTMLSurname] + astats[i] + [sum(astats[i])]
            for i in range(len(astats)) ]
            
        return (header, data)

    def get_average_authors_per_publication_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type].append(len(p.authors))
            except KeyError:
                ystats[p.year] = [[], [], [], []]
                ystats[p.year][p.pub_type].append(len(p.authors))

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(L) for L in ystats[y] ]
            + [ func(list(itertools.chain(*ystats[y]))) ]
            for y in ystats ]
        return (header, data)

    def get_publications_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                ystats[p.year][p.pub_type] += 1
            except KeyError:
                ystats[p.year] = [0, 0, 0, 0]
                ystats[p.year][p.pub_type] += 1

        data = [ [y] + ystats[y] + [sum(ystats[y])] for y in ystats ]
        return (header, data)

    def get_average_publications_per_author_by_year(self, av):
        header = ("Year", "Conference papers",
            "Journals", "Books",
            "Book chapers", "All publications")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year]
            except KeyError:
                s = np.zeros((len(self.authors), 4))
                ystats[p.year] = s
            for a in p.authors:
                s[a][p.pub_type] += 1

        func = Stat.FUNC[av]

        data = [ [y]
            + [ func(ystats[y][:, i]) for i in np.arange(4) ]
            + [ func(ystats[y].sum(axis=1)) ]
            for y in ystats ]
        return (header, data)

    def get_author_totals_by_year(self):
        header = ("Year", "Number of conference papers",
            "Number of journals", "Number of books",
            "Number of book chapers", "Total")

        ystats = {}
        for p in self.publications:
            try:
                s = ystats[p.year][p.pub_type]
            except KeyError:
                ystats[p.year] = [set(), set(), set(), set()]
                s = ystats[p.year][p.pub_type]
            for a in p.authors:
                s.add(a)
        data = [ [y] + [len(s) for s in ystats[y]] + [len(ystats[y][0] | ystats[y][1] | ystats[y][2] | ystats[y][3])]
            for y in ystats ]
        return (header, data)

    def add_publication(self, pub_type, title, year, authors):
        if year == None or len(authors) == 0:
            print "Warning: excluding publication due to missing information"
            print "    Publication type:", PublicationType[pub_type]
            print "    Title:", title
            print "    Year:", year
            print "    Authors:", ",".join(authors)
            return
        if title == None:
            print "Warning: adding publication with missing title [ %s %s (%s) ]" % (PublicationType[pub_type], year, ",".join(authors))
        idlist = []
        for a in authors:
            try:
                idlist.append(self.author_idx[a])
            except KeyError:
                a_id = len(self.authors)
                self.author_idx[a] = a_id
                idlist.append(a_id)
                self.authors.append(Author(a))
        self.publications.append(
            Publication(pub_type, title, year, idlist))
        if (len(self.publications) % 100000) == 0:
            print "Adding publication number %d (number of authors is %d)" % (len(self.publications), len(self.authors))

        if self.min_year == None or year < self.min_year:
            self.min_year = year
        if self.max_year == None or year > self.max_year:
            self.max_year = year

    def _get_collaborations(self, author_id, include_self):
        data = {}
        for p in self.publications:
            if author_id in p.authors:
                for a in p.authors:
                    try:
                        data[a] += 1
                    except KeyError:
                        data[a] = 1
        if not include_self:
            del data[author_id]
        return data

    def get_coauthor_details(self, name):
        author_id = self.author_idx[name]
        data = self._get_collaborations(author_id, True)
        return [ (self.authors[key].name, data[key])
            for key in data ]

    def get_network_data(self):
        na = len(self.authors)

        nodes = [ [self.authors[i].name, -1] for i in range(na) ]
        links = set()
        for a in range(na):
            collab = self._get_collaborations(a, False)
            nodes[a][1] = len(collab)
            for a2 in collab:
                if a < a2:
                    links.add((a, a2))
        return (nodes, links)
        
    #
    #   Return a dictionary of authors and the count of their
    #   appearance on a paper, first or last dependant upon the paramet
    #
    #   Params: pFirst - if true, count first occurence, else last
    #   
    def get_authors_position_count1(self, pFirst):
        data = {}
        for p in self.publications:
            if (p.pub_type == 0  or p.pub_type == 1  or p.pub_type == 2 or p.pub_type == 3): 
                authorid = p.authors[0]
                if not pFirst:
                    authorid = p.authors[len(p.authors)-1]
                if data.has_key(authorid): #author exist in dictionary?
                    data[authorid] += 1 #does, so increment
                else:   
                    data[authorid] = 1  #add it

        return data
        
    #
    #   Return a dictionary of authors and their various counts in an array
    #       for [CONFERENCE_PAPER, JOURNAL, BOOK, BOOK_CHAPTER, TOTAL]
    #
    #   Params: pSeachType: 0 = first, 1= last, 2 = solo
    #   
    def get_authors_position_count(self, pSeachType):
        data = {}
        for p in self.publications:
            if (p.pub_type == 0  or p.pub_type == 1  or p.pub_type == 2 or p.pub_type == 3): 
            
                authorid = -1
                
                if pSeachType == 0:  #first
                    authorid = p.authors[0]
                elif pSeachType == 1:  #last
                    authorid = p.authors[len(p.authors)-1]
                elif pSeachType == 2 and len (p.authors) == 1: #solo
                    authorid = p.authors[0]
                
                if authorid != -1: 
                    if data.has_key(authorid): #author exist in dictionary?
                        data[authorid][4]+= 1   #total 
                        data[authorid][p.pub_type]+= 1 #pub type
                    else:   
                        data[authorid] = [0,0,0,0,0]  #add it
                        data[authorid][4] = 1   #total number
                        data[authorid][p.pub_type] = 1 #pub type   

        return data

    #
    #   Return a 2d array of authors and the number of times they
    #   appear first on a paper
    #
    def get_paper_first_authors(self):
        data = self.get_authors_position_count(0)
        header = ("Author firstname", "Author surname", "First on paper count")

        #   Convert the dictionary into an array of arrays:
        #   one entry for each item, and each item contains
        #   an array of [authorName,firstAuthorCount]

        #modfied name to firstname / surname
        return (header,[[self.authors[row].HTMLFirstName,self.authors[row].HTMLSurname,data[row][4]] for row in data])

    #
    #   Return a 2d array of authors and the number of times they
    #   appear last on a paper
    #
    def get_paper_last_authors(self):
        data = self.get_authors_position_count(1)
        header = ("Author firstname", "Author surname", "Last on paper count")
        
        #   Convert the dictionary into an array of arrays:
        #   one entry for each item, and each item contains
        #   an array of [authorName,firstAuthorCount]

        #modfied name to firstname / surname
        return (header,[[self.authors[row].HTMLFirstName,self.authors[row].HTMLSurname,data[row][4]] for row in data])
        
    #
    #   Return a list of authors with the number of times they appear first and last 
    #   in the author list
    #
    #   AndyS refactored
    #    
    def get_paper_first_last_authors(self):
        data = {}
        header = ("Author firstname", "Author surname", "First on paper count", "Last on paper count")     
        
        firstAuthors = self.get_authors_position_count(0)
        lastAuthors = self.get_authors_position_count(1)        
        
        combinedList = {} #dictionary of authorID and two item array containing first and last scores
        
        for key in firstAuthors:
            combinedList[key] = [firstAuthors[key][4],0]

        for key in lastAuthors:
            if not combinedList.has_key(key):
                combinedList[key] = [0,lastAuthors[key][4]]  
            else:
                combinedList[key][1] = lastAuthors[key][4]
                
        return (header,[[self.authors[key].HTMLFirstName,self.authors[key].HTMLSurname,combinedList[key][0], combinedList[key][1]] for key in combinedList])
        

    #
    #   This is function to book count in publications
    #
    def get_publication_book_count(self,authorsname):
        
        bookCount = 0
        for p in self.publications:
           
            if (p.pub_type == 2): #book 
                for a in p.authors:
                  #print self.authors[a].name
                  #print self.authors[a].name
                  if(self.authors[a].name == authorsname):
                    bookCount += 1               

        return ("BookCount" , bookCount)

    #
    #   This is function to get coAuthor count in  all publications types
    #
    def get_coauthor_count(self,authorsname):
                       
        coAuthorCount = 0
                       
        header, coauthors=self.get_coauthor_data(None,None,4);  
        
        for c in coauthors:
           fullname = self.getName(c[0], c[1])
           if(fullname == authorsname):    
                coAuthorCount = len(c[3].split(','))
                break
            
                                                       
        return ("CoAuthor Count" , coAuthorCount)

    #
    #   This is function to find number of times the author appears first (overall)
    #
    def get_count_author_appears_first_overall(self,authorsname):
                
        data = self.get_authors_position_count(0)
               
        for row in data:
         fullname = self.authors[row].firstName + " " + self.authors[row].surname
         print fullname
         if(fullname == authorsname):
           #print fullname
           return ("Overall Count  of first appearence" ,  data[row][4])      
           
        return ("Overall Count  of first appearence" ,  0) 

    #
    #
    #
    def get_count_author_appears_last_overall(self,authorsname):
               
        data = self.get_authors_position_count(1)
               
        for row in data:
         fullname = self.authors[row].firstName + " " + self.authors[row].surname
         
         if(fullname == authorsname):
           return ("Overall Count  of last appearence" ,  data[row][4]) 
            
        return ("Overall Count  of last appearence" ,  0)

    #
    #
    #
    def get_all_results(self,authorsname):

       header= ("Criteria", "Result")
       data = []
        
       for r in self.search_by_author(authorsname):
            data.append(r)
            
       data.append(self.get_publication_book_count(authorsname))
       data.append(self.get_coauthor_count(authorsname))
       data.append(self.get_count_author_appears_first_overall(authorsname))
       data.append(self.get_count_author_appears_last_overall(authorsname))
      
       return (header, data)   
                   
    # Search through the names using the provided string and return
    # the first match we find
    #
    # Andy
    #
    def get_author_search(self, authorname):
    
        header = ("Match","cnt")
        
        matches = []
        for a in self.authors:
            if a.name.upper().find(authorname.upper()) > -1:               
                return a.name
    
        return None
        
    #
    #   search_by_author
    #
    #   Arthur
    #      
    def search_by_author(self, author_name):

        header, data = self.get_publications_by_author()
       
        result=[]

        for line in data:
         
            firstname, surname, paper, journal, book, book_chapter, overall = line           
 
            if self.getName( firstname, surname) == author_name:
                result.append(("Overall Publication",overall))
                result.append(("Number of conference papers",paper))
                result.append(("Number of journals",journal))
                result.append(("Number of book chapters",book_chapter))
                #result.append(("Number of book (ARTHUR)",book))
                #return (overall, paper, journal, book_chapter, book)                

        
        return result
        
    # 
    #   Get Full name from HTML
    #
    #   First name and surname are wrapped in an HTML <a> tag which is used
    #   to load the author_stats page and takes the form:
    #
    #   <a href='/author_stats?author_search=full+name'>firtsname</a>
    #   <a href='/author_stats?author_search=full+name'>lastname</a> 
    #
    def getName(self, firstName, surname):
        return (firstName[firstName.index(">")+1: firstName.rindex("<")] + 
            " " + surname[surname.index(">")+1: surname.rindex("<")]).strip()            

     
   
        
    #
    #   Calculate how many solo author papers an author has written.
    #
    #   Author: Sarah
    #
    #   Refactored by Andy
    #
    def get_paper_first_last_Solo_authors(self):
        data = {}
        header = ("Author firstname", "Author surname", "First on paper count", "Last on paper count", "Solo on paper count")    
        
        firstAuthors = self.get_authors_position_count(0)
        lastAuthors = self.get_authors_position_count(1)        
        soloAuthors = self.get_authors_position_count(2)           
        
        combinedList = {} #dictionary of authorID and three item array containing first, last scores and solo scores
        
        for key in firstAuthors:
            combinedList[key] = [firstAuthors[key][4],0,0]

        for key in lastAuthors:
            if not combinedList.has_key(key):
                combinedList[key] = [0,lastAuthors[key][4],0]  
            else:
                combinedList[key][1] = lastAuthors[key][4]

        for key in soloAuthors:
            if not combinedList.has_key(key):
                combinedList[key] = [0, 0, soloAuthors[key][4]]  
            else:
                combinedList[key][2] = soloAuthors[key][4]                
                
                
        return (header,[[self.authors[key].HTMLFirstName,self.authors[key].HTMLSurname,combinedList[key][0], combinedList[key][1], combinedList[key][2]] for key in combinedList])        

    def authorStats(self, author_name):
    
        results = []
        data = self.get_publications_by_author()#call to function in database.py
        header = ("Category", "Overall", "Journal Articles", "Conference papers", "Books", "Book Chapters")
                
        for line in data[1]:
         
            firstname, surname, paper, journal, book, book_chapter, overall = line   
            
            if self.getName( firstname, surname) == author_name: 
                results.append (["Number of publications", overall, journal,paper,book,book_chapter])
                break

        #First author 
        data = self.get_authors_position_count(0)      
        for key in data:

             # authorid
             # paper, journal, book, book_chapter, overall
            
            if self.authors[key].name == author_name: 
                results.append (["First author", data[key][4], data[key][1],data[key][0],data[key][2],data[key][3]])
                break        

        #Last author 
        data = self.get_authors_position_count(1)      
        for key in data:

             # authorid
             # paper, journal, book, book_chapter, overall
            
            if self.authors[key].name == author_name: 
                results.append (["Last author", data[key][4], data[key][1],data[key][0],data[key][2],data[key][3]])
                break                          
                    
        #Last author 
        data = self.get_authors_position_count(2)      
        for key in data:

             # authorid
             # paper, journal, book, book_chapter, overall
            
            if self.authors[key].name == author_name: 
                results.append (["Solo author", data[key][4], data[key][1],data[key][0],data[key][2],data[key][3]])
                break                          
                        
        #co-author
        co = self.get_coauthor_count(author_name)    
        results.append ([co[0], co[1]])
    
        return (header,results)
    
    #
    #   Calculate how many sole author, first author and last author papers an author has written, broken down by publication type.
    #
    def get_paper_first_last_solo_authors_by_publication_type(self, author_name):
        data = {}

        header = ("Author firstname", "Author surname",
                  "First on CONFERENCE PAPER", "First on JOURNAL", "First on BOOK", "First on BOOK CHAPTER",
                  "Last on CONFERENCE PAPER", "Last on  JOURNAL", "Last on BOOK", "Last on BOOK CHAPTER",
                  "Solo on  CONFERENCE PAPER", "Solo on   JOURNAL", "Solo on  BOOK", "Solo on  BOOK CHAPTER")

        print header

        # dictionaries

        firstAuthors = {}
        lastAuthors = {}
        soloAuthors = {}

        # add to the solo authors dictionary
        for p in self.publications:
            if len(p.authors) == 1 and self.authors[p.authors[0]].name == author_name:
                authorid = p.authors[0]
                if soloAuthors.has_key(authorid):
                    soloAuthors[authorid][p.pub_type] += 1
                else:
                    soloAuthors[authorid] = [0, 0, 0, 0]
                    soloAuthors[authorid][p.pub_type] = 1  # add it

                if not lastAuthors.has_key(authorid):  # author exist in lastAuthors?
                    lastAuthors[authorid] = [0, 0, 0, 0]  # add it

                if not firstAuthors.has_key(authorid):  # author exist in firstAuthors?
                    firstAuthors[authorid] = [0, 0, 0, 0]  # add it

        # start with the first author
        for p in self.publications:
            if self.authors[p.authors[0]].name == author_name:
                authorid = p.authors[0]
                if firstAuthors.has_key(authorid):  # author exist in firstAuthors?
                    firstAuthors[authorid][p.pub_type] += 1  # does, so increment
                else:
                    firstAuthors[authorid] = [0, 0, 0, 0]
                    firstAuthors[authorid][p.pub_type] = 1  # add it

                if not lastAuthors.has_key(authorid):  # author exist in lastAuthors?
                    lastAuthors[authorid] = [0, 0, 0, 0]  # add it

                if not soloAuthors.has_key(authorid):  # author exist in lastAuthors?
                    soloAuthors[authorid] = [0, 0, 0, 0]  # add it

        # add to the last authors dictionary
        for p in self.publications:
            if self.authors[p.authors[len(p.authors) - 1]].name == author_name: 
                authorid = p.authors[len(p.authors) - 1]
                if lastAuthors.has_key(authorid):  # author exist in dictionary?
                    lastAuthors[authorid][p.pub_type] += 1  # does, so increment
                else:
                    lastAuthors[authorid] = [0, 0, 0, 0]
                    lastAuthors[authorid][p.pub_type] = 1  # add it

                if not firstAuthors.has_key(authorid):  # author exist in firstAuthors?
                    firstAuthors[authorid] = [0, 0, 0, 0]  # add it

                if not soloAuthors.has_key(authorid):  # author exist in lastAuthors?
                    soloAuthors[authorid] = [0, 0, 0, 0]  # add it

        return (
            header
            , [[self.authors[row].HTMLFirstName, self.authors[row].HTMLSurname
                    , firstAuthors[row][0], firstAuthors[row][1], firstAuthors[row][2], firstAuthors[row][3]
                    , lastAuthors[row][0], lastAuthors[row][1], lastAuthors[row][2], lastAuthors[row][3]
                    , soloAuthors[row][0], soloAuthors[row][1], soloAuthors[row][2], soloAuthors[row][3]

                ] for row in firstAuthors
                ]
        )
    #
    #   Calculate the degrees of separation between the two names
    #
    def separation(self, name1, name2):
    
        header = ("Author1", "Author2", "Degrees of Separation")    
                                            
        def flattenList (pList):
            foo =[self.authors[item].name for sublist in pList for item in sublist]
            return ", ".join(foo)
        
        def getPubs (pAuthor, pPubExclude):
            return [p for p in self.publications if pAuthor in p.authors and not p in pPubExclude]
                
                
        #
        #   Recursive routine
        #
                
        routeCount = {}#dictionary of separation and their counts 
                
               
        def degreeSeparation(pStart, pFinish, pVisitedAuthors, pVisitedPubs, pDepth):
                                
            #if not pStart in pVisitedAuthors:
            #    pVisitedAuthors.append(pStart)  
                
            print "Depth: {0}, visited authors:{1}, visited pubs:{2}".format(pDepth, len (pVisitedAuthors), len(pVisitedPubs))
                                
            #get the pubs associated with the pStart author
            pubs = getPubs(pStart, pVisitedPubs)
            
            #print  flattenList(pubs)
                        
            for p in pubs:  #examine each publication
                 
                if not p in pVisitedPubs:
                    pVisitedPubs.append(p)                   
                    
                    for a in p.authors:
                        
                        if a == pFinish:
                                                        
                            path = "/".join(map(str,pVisitedAuthors + [pFinish])) 
                            
                            if routeCount.has_key(path):
                                routeCount[path]+=1
                            else:
                                routeCount[path]=1
                                
                            return
                                                                
                        elif not a in pVisitedAuthors:
                            
                            newList = list (pVisitedAuthors)
                            newList.append(a)
                            newPubs = list (pVisitedPubs)    
    
                            degreeSeparation(a,pFinish, newList, newPubs , pDepth+1)                   
          
        degreeSeparation (name1,name2,[],[],0)  

        sep = "X"
        
        if len(routeCount) > 0:#no connection
            
            # The shortest path contains the lowest number of slashs.
            # A value of one indicates that they are in the same pub 
        
            count = []
            
            for k in routeCount:
                count.append (k.count("/"))
                
            sep =  str(min (count) - 1)
     
        
        
        data = [[self.authors[int(name1)].HTMLName, self.authors[int(name2)].HTMLName, sep]]
        
                        
        return (header, data)
        
  
    #return the ratio of similarity between the two strings
    def similar(searchString, substring):
      return SequenceMatcher(None, searchString.lower(), substring.lower()).ratio()

  
    def search_author_names(self, search_name):

        lst=[]
        for a in self.authors:
          lst.append([a.firstName, a.surname])
        
       #filter list for names that contain search terms
	matches = [x for x in lst if search_name.lower() in (x[0] + x[1]).lower()]
        
       
	  
	  #No matchers
	notmatches  = [x for x in lst if search_name.lower() not in (x[0] + x[1]).lower()]
	  
	  #
	  # Sort the list using lamdba, with a search precedence of
	  #   Surname starts with search term
	  #   Any Firstname starts with search term
	  #   Similarity ratio of surname to search term
	  #   Similarity ratio of firstname to search term
	  #
	results = sorted(matches, key = lambda name: 
	    (
	      name[1].lower().startswith(search_name.lower())   
	      , any(item.lower().startswith(search_name.lower()) for item in name[0].split()) 
	      , SequenceMatcher(None, name[0].lower(), search_name.lower()).ratio()
	      , SequenceMatcher(None, name[1].lower(), search_name.lower()).ratio()
	    )
	    , reverse = True)
	  
	 #results.extend(notmatches) #add the no matches   
       
        print results
	  
	return results     
    
    
 

class DocumentHandler(handler.ContentHandler):
    TITLE_TAGS = [ "sub", "sup", "i", "tt", "ref" ]
    PUB_TYPE = {
        "inproceedings":Publication.CONFERENCE_PAPER,
        "article":Publication.JOURNAL,
        "book":Publication.BOOK,
        "incollection":Publication.BOOK_CHAPTER }

    def __init__(self, db):
        self.tag = None
        self.chrs = ""
        self.clearData()
        self.db = db

    def clearData(self):
        self.pub_type = None
        self.authors = []
        self.year = None
        self.title = None

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, name, attrs):
        if name in self.TITLE_TAGS:
            return
        if name in DocumentHandler.PUB_TYPE.keys():
            self.pub_type = DocumentHandler.PUB_TYPE[name]
        self.tag = name
        self.chrs = ""

    def endElement(self, name):
        if self.pub_type == None:
            return
        if name in self.TITLE_TAGS:
            return
        d = self.chrs.strip()
        if self.tag == "author":
            self.authors.append(d)
        elif self.tag == "title":
            self.title = d
        elif self.tag == "year":
            self.year = int(d)
        elif name in DocumentHandler.PUB_TYPE.keys():
            self.db.add_publication(
                self.pub_type,
                self.title,
                self.year,
                self.authors)
            self.clearData()
        self.tag = None
        self.chrs = ""

    def characters(self, chrs):
        if self.pub_type != None:
            self.chrs += chrs
            

