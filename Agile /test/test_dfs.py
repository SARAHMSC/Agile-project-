from os import path
import unittest

from comp62521.database import database

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        dir, _ = path.split(__file__)
        self.data_dir = path.join(dir, "..", "data")

#     def test_read(self):
#         db = database.Database()
#         self.assertTrue(db.read(path.join(self.data_dir, "simple.xml")))
#         self.assertEqual(len(db.publications), 1)    
    
    def test_bong(self):
        db = database.Database()      
        db.read(path.join(self.data_dir, "dblp_2000_2005_114_papers.xml"))
        pubs = db.publications
                 
        #head, data = db.separation(db.get_author_index("Stefano Ceri"), db.get_author_index("Piero Fraternali"))
        
        #print db.get_author_index("Robert Haines")
        #print db.get_author_index("Yeliz Yesilada")
        
#         for a in db.get_all_authors_sorted():
#                 if 3 != a[0]:
#                     print  db.separation(3, a[0])[1]
        
        #for p in pubs:
        #    print "{0}: {1}".format(pubs.index(p), map(str,p.authors ))
        
        #print db.get_all_authors()
                
        head, data = db.separation(10, 11)
        
        for p in pubs:
            if 3 in p.authors and 91 in p.authors:
                print "jO"
        
        print data
 
if __name__ == '__main__':
    unittest.main()
