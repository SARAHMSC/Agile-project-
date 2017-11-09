#
#	This file contains the function definitions used to compute
#	the statistics for 
#		Publication Summary, 
#		Publication by Author, 
#		Publication by Year, 
#		Author by Year, 
#		Averaged Year Data
#		Co-Authors
#
#

from comp62521 import app
from database import database
from flask import (render_template, request)

def format_data(data):
    fmt = "%.2f"
    result = []
    for item in data:
        if type(item) is list:
            result.append(", ".join([ (fmt % i).rstrip('0').rstrip('.') for i in item ]))
        else:
            result.append((fmt % item).rstrip('0').rstrip('.'))
    return result

#
#	Handles "Averaged Year Data"
#
@app.route("/averages")
def showAverages():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"averages"}
    args['title'] = "Averaged Data"
    args["startCol"]=0
    tables = []
    headers = ["Average", "Conference Paper", "Journal", "Book", "Book Chapter", "All Publications"]
    averages = [ database.Stat.MEAN, database.Stat.MEDIAN, database.Stat.MODE ]
    tables.append({
        "id":1,
        "title":"Average Authors per Publication",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_per_publication(i)[1])#call to function in database.py
                for i in averages ] })
    tables.append({
        "id":2,
        "title":"Average Publications per Author",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_per_author(i)[1])#call to function in database.py
                for i in averages ] })
    tables.append({
        "id":3,
        "title":"Average Publications in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_publications_in_a_year(i)[1])#call to function in database.py
                for i in averages ] })
    tables.append({
        "id":4,
        "title":"Average Authors in a Year",
        "header":headers,
        "rows":[
                [ database.Stat.STR[i] ]
                + format_data(db.get_average_authors_in_a_year(i)[1])#call to function in database.py
                for i in averages ] })

    args['tables'] = tables
    return render_template("averages.html", args=args)
	
#
#	Handlers "PaperFirstAuthor"
#
#	Andy Stobirski 13/11/2016
#
@app.route("/paperfirstauthor")
def showPaperFirstAuthor():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"firstauthors"}
    args["title"] = "First Paper Author Count"	
    args["startCol"]=1
	
    args["data"] = db.get_paper_first_authors()   #call to function in database.py

    return render_template('statistics_details_multicolumnsort.html', args=args)
	
#
#	Handlers "PaperLastAuthor"
#
#	Andy Stobirski 13/11/2016
#
@app.route("/paperlastauthor")
def showPaperLastAuthor():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"firstauthors"}
    args["title"] = "Last Paper Author Count"	
    args["startCol"]=1
	
    args["data"] = db.get_paper_last_authors()   #call to function in database.py

    return render_template('statistics_details_multicolumnsort.html', args=args)	

	
#
#	Handlers "paperfirstlastauthor"
#
#	Andy Stobirski 13/11/2016
#
@app.route("/paperfirstlastauthor")
def showPaperFirstLastAuthor():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"firstauthors"}
    args["title"] = "First and Last Paper Author Count"	
    args["startCol"]=1
	
    args["data"] = db.get_paper_first_last_authors()   #call to function in database.py

    return render_template('statistics_details_sort.html', args=args)		
    
    
#
#	Handlers "authorsearch"
#
#	Andy Stobirski 19/11/2016
#
@app.route("/authorsearch")
def showAuthorSearch():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":"authorsearch"}
    args["title"] = "Author Search"
    args["startCol"]=0	
	    
    matchName = None
    if "author_search" in request.args:	
        matchName = db.get_author_search(request.args.get("author_search")) 
        
    if (matchName != None):
        args["name"] = database.Author.MakeFullName(matchName)
        
	args["data"]=db.get_all_results(matchName)
       
        
    else:
        #nothing found
        args["data"]=[]
        
        
    return render_template('AuthorSearch.html', args=args)		


#
#	Handles "Co-Authors"
#
@app.route("/coauthors")
def showCoAuthors():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    PUB_TYPES = ["Conference Papers", "Journals", "Books", "Book Chapters", "All Publications"]
    args = {"dataset":dataset, "id":"coauthors"}
    args["title"] = "Co-Authors"

    start_year = db.min_year
    if "start_year" in request.args:
        start_year = int(request.args.get("start_year"))

    end_year = db.max_year
    if "end_year" in request.args:
        end_year = int(request.args.get("end_year"))

    pub_type = 4
    if "pub_type" in request.args:
        pub_type = int(request.args.get("pub_type"))

    args["data"] = db.get_coauthor_data(start_year, end_year, pub_type)#call to function in database.py
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_type"] = pub_type
    args["min_year"] = db.min_year
    args["max_year"] = db.max_year
    args["start_year"] = start_year
    args["end_year"] = end_year
    args["pub_str"] = PUB_TYPES[pub_type]
    return render_template("coauthors.html", args=args)

#	
#	Load the first page
#
#	Examine the hyperlinks in "statistics.html" - they reference the definitions
#	stored in @app.route("<somearg>") above and below
#
@app.route("/")
def showStatisticsMenu():
    dataset = app.config['DATASET']
    args = {"dataset":dataset}
    
    return render_template('statistics.html', args=args)

#
#	This handles: "Publication Summary", "Publication by Author", 
#		"Publication by Year", "Author by Year"
#	
@app.route("/statisticsdetails/<status>")
def showPublicationSummary(status):
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset":dataset, "id":status}
    args["startCol"]=0

    if (status == "publication_summary"):
        args["title"] = "Publication Summary"
        args["data"] = db.get_publication_summary()	#call to function in database.py

    if (status == "publication_author"):
        args["title"] = "Author Publication"
        args["startCol"]=1
        args["data"] = db.get_publications_by_author()#call to function in database.py

    if (status == "publication_year"):
        args["title"] = "Publication by Year"
        args["data"] = db.get_publications_by_year()#call to function in database.py

    if (status == "author_year"):
        args["title"] = "Author by Year"
        args["data"] = db.get_author_totals_by_year()#call to function in database.py

    return render_template('statistics_details.html', args=args)
    
 #
 #  search_by_author
 #
 #  Arthur
 #
@app.route("/search_by_author")
def search_by_author():
    print "JLJLKJL";
    args = {}
    db = app.config['DATABASE']
    author_name = request.args.get('author_name', '')
    args['author_name'] = author_name
    args["startCol"]=0
    if author_name:
        overall, paper, journal, book_chapter, book = db.search_by_author(author_name)

        args['overall'] = overall
        args['paper'] = paper
        args['journal'] = journal
        args['book_chapter'] = book_chapter
        args['book'] = book

    return render_template('search_by_author.html', args=args)
    
@app.route("/paperfirstlastsoloauthor")
def showPaperFirstLastsoloAuthor():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": "firstauthors"}
    args["title"] = "First, Last and Solo Paper Author Count"
    args["startCol"]=1

    args["data"] = db.get_paper_first_last_Solo_authors() # call to function in database.py

    return render_template('statistics_details_sort.html', args=args)
    
@app.route("/author_stats")
def showAuthorStats():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": "firstauthors"}
    args["title"] = "Author stats for BLANK"
    args["data"] = None
    args["startCol"]=0
    
    if "author_search" in request.args:
        if len(request.args.get("author_search"))> 0:
            args["title"] = "Author stats for " + request.args.get("author_search")
            args["data"] = db.authorStats(request.args.get("author_search"))
        
    return render_template("statistics_details_sort.html", args=args)
    
@app.route("/paperfirstlastsoloauthorbypublicationtype")
def showPaperFirstLastsoloAuthorByPublicationType():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": "authorsearch"}
    args["title"] = "First, Last and Solo Paper Author Count By Publication type"
    args["startCol"]=1

    matchName = None
    if "author_search" in request.args:
        matchName = db.get_author_search(request.args.get("author_search"))

    if (matchName != None):
        args["name"] = database.Author.MakeFullName(matchName)

        args["data"] = db.get_paper_first_last_solo_authors_by_publication_type(matchName) # call to function in database.py

    else:
        # nothing found
        args["data"] = []


    return render_template('AuthersearchByPublication.html', args=args)


@app.route("/authorsearch2")
def AuthorSearch2():
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": "firstauthors"}
    args["title"] = "Author stats for BLANK"
    args["data"] = None
    args["startCol"]=0

    
    search_name = request.args.get('search_name', '').strip().lower()

    if search_name:
        
        names = db.search_author_names(search_name)
        
    else:
        names = []
    
    if len(names) == 1:
        args["title"] = "Author stats for " + names[0][0] + " "  + names[0][1]
        args["data"] = db.authorStats(names[0][0] + " "  + names[0][1])
        
    elif len(names) > 1:
        args["title"] = "Search results for: " + request.args.get("search_name")
        args["data"] = (("Author Name",""), [[name[2]] for name in names])

                
    return render_template('AuthorSearch2.html', args=args)

@app.route("/separation")
def separation():    
    dataset = app.config['DATASET']
    db = app.config['DATABASE']
    args = {"dataset": dataset, "id": "authorsearch"}
    args["title"] = "Degrees of Separation"
    
    args["names"] = db.get_all_authors_sorted()

    args["authors"] = [-1,-1]
    
    print "views.py: separation called"
    
    if request.args.get("author1") != request.args.get("author2"):    
	args["authors"] = [int(request.args.get("author1")), int(request.args.get("author2"))]
        args["data"] = db.separation(int(request.args.get("author1")), int(request.args.get("author2")))
    else:
        args["data"] = []

    
    return render_template('Separation.html', args=args)
    
    
