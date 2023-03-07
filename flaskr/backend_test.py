from flaskr.backend import Backend

# TODO(Project 1): Write tests for Backend methods.
import unittest
from unittest.mock import Mock, MagicMock, mock_open, patch
from .backend import Backend

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.bucket_name = 'test-bucket' #mock bucket
        self.backend = Backend(self.bucket_name) #inject the mock bucket
        self.mock_blob = MagicMock() #create mock blob
        #mockblob characteristics for the tests
        self.mock_blob.return_value = self.mock_blob 
        self.mock_blob.exists.return_value = False
        self.mock_blob.upload_from_string.return_value = None

        #mock blobs for many pages with names and types
        self.mock_blob1 = MagicMock()
        self.mock_blob1.name = 'page1'
        self.mock_blob1.content_type = 'text'
        
        self.mock_blob2 = MagicMock()
        self.mock_blob2.name = 'page2'
        self.mock_blob2.content_type = 'image'
        
        self.mock_blob3 = MagicMock()
        self.mock_blob3.name = 'page3'
        self.mock_blob3.content_type = 'text'
        
        self.mock_blobs = [self.mock_blob1, self.mock_blob2, self.mock_blob3] #mock bucket with the pages

    def test_upload(self):
        self.mock_blob.exists.return_value = True
        self.mock_blob.download_as_string.return_value = b'test title'
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob)
        with patch("builtins.open", mock_open(read_data=b'test title')) as mock_file:
            fake_file = open("fakefile")
            fake_file.content_type = '.txt'
            self.backend.upload('test-game', fake_file)
            assert self.backend.get_wiki_page('test-game') == b'test title'
        mock_file.assert_called_with("fakefile")
    
    def test_get_image(self):
        name = 'test-image'
        mock_blob1 = MagicMock()
        mock_blob1.name = "test1"
        mock_blob2 = MagicMock()
        mock_blob2.name = name
        mock_blob3 = MagicMock()
        mock_blob3.name = "test3"
        mock_blobs = MagicMock()
        mock_blobs.return_value = iter({mock_blob1,mock_blob2,mock_blob3})
        self.backend.storage_client.list_blobs = mock_blobs
        with patch("builtins.open", mock_open(read_data=b'img data')) as mock_file:
            result = self.backend.get_image(name, open(mock_blob2))
            assert 'data:image' in result
    
    def test_get_wiki_page_exists(self):

        name = 'test-page' #set the mock blob name to test-page
        self.mock_blob.exists.return_value = True #set it so that it return true when asked if exists.
        self.mock_blob.download_as_string.return_value = b'Test content' #set it so that it returns this string
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob) #inject it

        result = self.backend.get_wiki_page(name) #save the result after calling the function

        self.assertEqual(result, b'Test content') #assert


    def test_get_wiki_page_not_exists(self):

        name = 'non-page'#set the mock blob name to non-page
        self.mock_blob.exists.return_value = False #set it so that it return false when asked if exists.
        self.backend.bucket.blob = MagicMock(return_value=self.mock_blob) #inject it

        result = self.backend.get_wiki_page(name) #save the result after calling the function

        self.assertEqual(result, None) #assert
    

    def test_get_all_page_names(self):

        mock_list_blobs = MagicMock()# list of pages self.mock_blobs = [self.mock_blob1, self.mock_blob2, self.mock_blob3]
        mock_list_blobs.return_value = iter(self.mock_blobs) #make so that it return the blobs list
        self.backend.storage_client.list_blobs = mock_list_blobs #inject it

        expected_result = {'page1': self.mock_blob1, 'page3': self.mock_blob3} #what it should return

        result = self.backend.get_all_page_names() #save the output after calling the function

        self.assertEqual(result, expected_result) #assert
        
if __name__ == 'main':
    unittest.main()