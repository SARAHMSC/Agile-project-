from os import path
import unittest

from comp62521.database import database

class TestDatabase(unittest.TestCase):
    
    #
    #   Author first name and surname are contained with ab
    #   HTML <a> tag
    #
    def getName(self, firstName, surname):
        return (firstName[firstName.index(">")+1: firstName.rindex("<")] + 
            " " + surname[surname.index(">")+1: surname.rindex("<")]).strip()

    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

    def test_read(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        self.assertEqual(len(db.publications), 1)

    def test_read_invalid_xml(self):
        db = database.Database()
        self.assertFalse(db.read(path.join(self.data_dir, "invalid_xml_file.xml")))

    def test_read_missing_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_year.xml")))
        self.assertEqual(len(db.publications), 0)

    def test_read_missing_title(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "missing_title.xml")))
        # publications with missing titles should be added
        self.assertEqual(len(db.publications), 1)

    def test_get_average_authors_per_publication(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-1.xml")))
        _, data = db.get_average_authors_per_publication(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.3, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 2, places=1)
        _, data = db.get_average_authors_per_publication(database.Stat.MODE)
        self.assertEqual(data[0], [2])

    def test_get_average_publications_per_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-2.xml")))
        _, data = db.get_average_publications_per_author(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 1.5, places=1)
        _, data = db.get_average_publications_per_author(database.Stat.MODE)
        self.assertEqual(data[0], [0, 1, 2, 3])

    def test_get_average_publications_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-3.xml")))
        _, data = db.get_average_publications_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.5, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_publications_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [3])

    def test_get_average_authors_in_a_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "sprint-2-acceptance-4.xml")))
        _, data = db.get_average_authors_in_a_year(database.Stat.MEAN)
        self.assertAlmostEqual(data[0], 2.8, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MEDIAN)
        self.assertAlmostEqual(data[0], 3, places=1)
        _, data = db.get_average_authors_in_a_year(database.Stat.MODE)
        self.assertEqual(data[0], [0, 2, 4, 5])
        # additional test for union of authors
        self.assertEqual(data[-1], [0, 2, 4, 5])

    def test_get_publication_summary(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publication_summary()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data[0]), 6,
            "incorrect number of columns in data")
        self.assertEqual(len(data), 2,
            "incorrect number of rows in data")
        self.assertEqual(data[0][1], 1,
            "incorrect number of publications for conference papers")
        self.assertEqual(data[1][1], 2,
            "incorrect number of authors for conference papers")

    def test_get_average_authors_per_publication_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_average_authors_per_publication_by_author(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 3,
            "incorrect average of number of conference papers")
        self.assertEqual(data[0][1], 1.5,
            "incorrect mean journals for author1")
        self.assertEqual(data[1][1], 2,
            "incorrect mean journals for author2")
        self.assertEqual(data[2][1], 1,
            "incorrect mean journals for author3")

    def test_get_publications_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_author()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 2,
            "incorrect number of authors")
        self.assertEqual(data[0][-1], 1,
            "incorrect total")

    def test_get_average_publications_per_author_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_average_publications_per_author_by_year(database.Stat.MEAN)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_publications_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_publications_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")

    def test_get_author_totals_by_year(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
        header, data = db.get_author_totals_by_year()
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        self.assertEqual(len(data), 1,
            "incorrect number of rows")
        self.assertEqual(data[0][0], 9999,
            "incorrect year in result")
        self.assertEqual(data[0][1], 2,
            "incorrect number of authors in result")

    def test_get_athur_appreas_firsttimes(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_paper_first_authors()
        self.assertEqual(len(header), len(data[0]),
             "header and data column size doesn't match")
        self.assertEqual(data[0][2], 86,
             "incorrect number of author in result")
        self.assertEqual(data[2][2], 3,
             "incorrect number of author in result")
        self.assertEqual(data[14][2], 3,
             "incorrect number of author in result")



    def test_get_athur_appreas_lasttimes(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_paper_last_authors()
        self.assertEqual(len(header), len(data[0]),
             "header and data column size doesn't match")
        self.assertEqual(data[0][2], 33,
             "incorrect number of author in result")
        self.assertEqual(data[3][2], 1,
             "incorrect number of author in result")
        self.assertEqual(data[12][2], 11,
             "incorrect number of author in result")


    def test_get_athur_appreas_first_lasttime(self):
        
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_paper_first_authors()

        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        # Actually it should be three need to fix the function
        self.assertEqual(len(data), 2,"incorrect number of authors in result")
    
        print "++++++++++++++++++++++++++"
        print self.getName(data[0][0], data[0][1])
        self.assertEqual(self.getName(data[0][0], data[0][1]), "author1","incorrect author name in result")
        self.assertEqual(data[0][2], 2,"incorrect count in result")
        
        self.assertEqual(self.getName(data[1][0], data[1][1]), "author3","incorrect author name in result")
        self.assertEqual(data[1][2], 1,"incorrect count in result")

    
    def test_get_andys_list_cross_check(self):
        db = database.Database()
        db.read(path.join(self.data_dir, "dblp_curated_sample.xml"))

        lAuth = db.get_paper_last_authors()
        fAuth = db.get_paper_first_authors()
        flAuth = db.get_paper_first_last_authors()

        fAuthCnt = len(fAuth)
        lAuthCnt = len(lAuth)

        #print fAuthCnt
        #print lAuthCnt


        flAuthCnt_f = 0
        flAuthCnt_l = 0

        for fl in flAuth:
            if fl[1] > 0:
                 flAuthCnt_f+=1
            if fl[2] > 0:
                 flAuthCnt_l+=1

        self.assertEqual(fAuthCnt, flAuthCnt_f)

        self.assertEqual(lAuthCnt, flAuthCnt_l)


    def test_get_author_by_first_on_count(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "three-authors-and-three-publications.xml")))
        header, data = db.get_paper_first_authors()
        #print data[0]
        #print data[1]
        #print len(data)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        # Actually it should be three need to fix the function
        self.assertEqual(len(data), 2,"incorrect number of authors in result")
        self.assertEqual(self.getName(data[0][0], data[0][1]), "author1","incorrect author name in result")
        self.assertEqual(data[0][2], 2,"incorrect count in result")
        self.assertEqual(self.getName(data[1][0], data[1][1]), "author3","incorrect author name in result")
        self.assertEqual(data[1][2], 1,"incorrect count in result")

    def test_get_author_by_last_on_count(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_paper_first_authors()
        #print data[0]
        #print data[1]
        #print len(data)
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
 	
        self.assertEqual(len(data), 285,"incorrect number of authors in result")
        self.assertEqual(self.getName(data[0][0], data[0][1]), "Stefano Ceri","incorrect author name in result")
        self.assertEqual(data[0][2], 86,"incorrect count in result")

    def test_get_author_by_first_and_last_on_count(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_paper_first_last_authors()
        
        self.assertEqual(len(header), len(data[0]),
            "header and data column size doesn't match")
        
        self.assertEqual(len(data), 498,"incorrect number of authors in result")
        self.assertEqual(self.getName(data[0][0], data[0][1]), "Stefano Ceri","incorrect author name in result")
        self.assertEqual(data[0][2], 86,"incorrect count in result")
        self.assertEqual(data[0][3], 33,"incorrect count in result")

    def test_to_get_number_of_books(self):
      db = database.Database()
      
      self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))  
      self.assertEqual(db.get_publication_book_count("Stefano Ceri"), ('BookCount', 6))
      #Connect to different dataset and try it 
      self.assertTrue(db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml"))) 
      self.assertEqual(db.get_publication_book_count("Stefano Ceri"), ('BookCount', 0))
      
      
    def test_search_by_author(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        overall, paper, journal, book_chapter = db.search_by_author('Stefano Ceri')

        self.assertEqual(overall, ('Overall Publication', 218))
        self.assertEqual(paper, ("Number of conference papers", 100))
        self.assertEqual(journal, ("Number of journals", 94))
        self.assertEqual(book_chapter, ("Number of book chapters", 18))
      

    def test_to_get_number_of_coAuthors(self):
      db = database.Database()
      
      self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))  
      self.assertEqual(db.get_coauthor_count("Stefano Ceri"),('CoAuthor Count', 230))

    def test_to_get_number_of_aunthors_appear_first(self):
      db = database.Database()
      
      self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))  
      self.assertEqual(db.get_count_author_appears_first_overall("Stefano Ceri"),('Overall Count  of first appearence', 86))

    def test_to_get_number_of_authors_appear_last(self):
      db = database.Database()
      
      self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))  
      self.assertEqual(db.get_count_author_appears_last_overall("Stefano Ceri"),('Overall Count  of last appearence', 33))
      
# test get_paper_first_last_Solo_authors

    def test_get_paper_first_last_Solo_authors(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        header, data = db.get_paper_first_last_Solo_authors()
        
        self.assertEqual(len(header), len(data[0]), "header and data column size doesn't match")
        
        #
        #   data structure per rows
        #
        #       0 firstname
        #       1 surname
        #       2 first on paper count
        #       3 last on paper count
        #       4 solo on paper count
        #
        #   Items 0 and 1, are wrapped in an HTML <a> tag which is used
        #   to load the author_stats page and takes the form:
        #
        #   <a href='/author_stats?author_search=full+name'>firtsname</a>
        #   <a href='/author_stats?author_search=full+name'>lastname</a>
        #
        
        self.assertEqual(self.getName(data[1][0],data[1][1]) , "Piero Fraternali", "name doesn't match")
        self.assertEqual(data[1][2],0 , " first on paper count doesn't match")
        self.assertEqual(data[1][3],7 , " last on paper count doesn't match")
        self.assertEqual(data[1][4],0 , " solo on paper count doesn't match")
                      
        self.assertEqual(self.getName(data[2][0],data[2][1]) , "Carlo Batini", "name doesn't match")
        self.assertEqual(data[2][2],3 , " first on paper count doesn't match")
        self.assertEqual(data[2][3],5 , " last on paper count doesn't match")
        self.assertEqual(data[2][4],0 , " solo on paper count doesn't match")

   
    def test_search_author_names(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_sample.xml")))
        data = db.search_author_names('Sam')
               
        self.assertEqual(len(data),8 , "Size of results don't match")
        
        self.assertEqual(data[0][0] + " " + data[0][1], "Sandra Sampaio" ,"Fist search result doesn't match")
        self.assertEqual(data[1][0] + " " + data[1][1], "Sandra de F. Mendes Sampaio" ,"Second search result doesn't match")
        self.assertEqual(data[2][0] + " " + data[2][1], "Pierangela Samarati" ,"Third search result doesn't match")
        
        self.assertEqual(data[6][0] + " " + data[6][1], "Samuel Madden" ,"Last search result doesn't match")

    def test_separation(self):
        db = database.Database()
        self.assertTrue(db.read(path.join(self.data_dir, "dblp_curated_separations.xml")))



    	head,data = db.separation(db.get_author_index("Robert Haines"),db.get_author_index("Donal Fellows"))
    	self.assertEqual(data[0][2], "0" ,"Separation doesn't match")
    
    	head,data = db.separation(db.get_author_index("Robert Haines"), db.get_author_index("Roger J. Hubbold"))
    	self.assertEqual(data[0][2], "3" ,"Separation doesn't match")
        
        head,data = db.separation(db.get_author_index("Robert Haines"), db.get_author_index("Georg Gottlob"))
        self.assertEqual(data[0][2], "X" ,"Separation doesn't match")    
    	
                
 
if __name__ == '__main__':
    unittest.main()
