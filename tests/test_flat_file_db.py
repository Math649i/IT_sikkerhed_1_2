import unittest
import os
import sys

# Tilføj src til stien, så vi kan importere FlatFileDB
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from flat_file_db import FlatFileDB

class TestFlatFileDB(unittest.TestCase):
    def setUp(self):
        self.test_filename = 'test_db.json'
        self.db = FlatFileDB(self.test_filename)
        self.sample_user = {
            'person_id': '123',
            'first_name': 'John',
            'last_name': 'Doe',
            'address': 'Main St',
            'street_number': '1',
            'password': 'secret_password',
            'enabled': True
        }

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_add_user(self):
        # Risiko: Hvis oprettelse af bruger fejler uden feedback, kan det føre til datatab eller brugerfrustration.
        # Given: En ny bruger med gyldige data
        user_data = self.sample_user
        
        # When: Brugeren tilføjes til databasen
        self.db.add_user(user_data)
        
        # Then: Brugeren skal kunne hentes og matche inputdata
        retrieved_user = self.db.get_user('123')
        self.assertEqual(retrieved_user, user_data)

    def test_add_duplicate_user(self):
         # Risiko: Dublerede ID'er kan føre til datakorruption og forkert brugeridentifikation.
        # Given: En bruger findes allerede i databasen
        self.db.add_user(self.sample_user)
        
        # When: Der forsøges at tilføje en anden bruger med samme ID
        # Then: En ValueError skal kastes
        with self.assertRaises(ValueError):
            self.db.add_user(self.sample_user)

    def test_get_nonexistent_user(self):
        # Risiko: Systemet kan gå ned eller returnere forkerte data, hvis håndtering af manglende brugere er dårlig.
        # Given: En tom database
        
        # When: Der anmodes om en bruger med et ID, der ikke findes
        user = self.db.get_user('999')
        
        # Then: Resultatet skal være None
        self.assertIsNone(user)

    def test_update_user(self):
        # Risiko: Hvis opdateringer fejler stille, kan brugere tro, at deres information er opdateret, når den ikke er det.
        # Given: En bruger findes i databasen
        self.db.add_user(self.sample_user)
        updates = {'first_name': 'Jane', 'enabled': False}
        
        # When: Brugerens information opdateres
        self.db.update_user('123', updates)
        
        # Then: Brugerens data skal afspejle ændringerne
        updated_user = self.db.get_user('123')
        self.assertEqual(updated_user['first_name'], 'Jane')
        self.assertFalse(updated_user['enabled'])
        
    def test_delete_user(self):
        # Risiko: Hvis sletning fejler, kan vi beholde data længere end GDPR tillader eller holde deaktiverede brugere aktive.
        # Given: En bruger findes i databasen
        self.db.add_user(self.sample_user)
        
        # When: Brugeren slettes
        self.db.delete_user('123')
        
        # Then: Brugeren skal ikke længere findes i databasen
        self.assertIsNone(self.db.get_user('123'))

    def test_missing_fields(self):
        # Risiko: Ufuldstændige brugerprofiler kan forårsage applikationsfejl eller logikfejl senere.
        # Given: Brugerdata med et manglende påkrævet felt (f.eks. adgangskode)
        incomplete_user = self.sample_user.copy()
        del incomplete_user['password']
        
        # When: Der forsøges at tilføje den ufuldstændige bruger
        # Then: En ValueError skal kastes
        with self.assertRaisesRegex(ValueError, "Missing required field: password"):
            self.db.add_user(incomplete_user)

if __name__ == '__main__':
    unittest.main()
