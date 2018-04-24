import sys
import os
import unittest
from mock import patch, mock_open
from ads import Service, ServiceSet, Cache, _load_spec_file

class MockDevice():
    """MockDevice to suppress stdout"""

    @classmethod 
    def flush(s): pass
    
    def write(self, s): pass

class TestCache(unittest.TestCase):

    def setUp(self):
        self.cachefile = ".ads_cache.yml"
        self.project_file = "/adsroot/adsroot.yml"
        self.profile_dir = "/profile"
        self.service_sets = [ServiceSet("service1", ["service1"]),
                        ServiceSet("service1", ["service2"])]
        self.map = {"adsroot": self.project_file,
                    "service1": "/adsroot/service1/ads.yml",
                    "service2": "/adsroot/service2/ads.yml"}
        self.read_data = "adsroot: /adsroot/adsroot.yml\n"\
                       + "service1: /adsroot/service1/ads.yml\n"\
                       + "service2: /adsroot/service2/ads.yml\n"

    def test_get_cache_path(self):
        default_home = "/default"
        self.assertEqual(
            Cache.get_cache_path(default_home),
            "%s/.ads_cache.yml" % (default_home)
        )

    def test_get_cache_path_with_env_var(self):
        default_home = "/default"
        cache_home = "/ads_cache_home"
        os.environ["ADS_CACHE_HOME"] = cache_home
        self.assertEqual(
            Cache.get_cache_path(default_home),
            "%s/.ads_cache.yml" % (cache_home)
        )

    def test_load_from_cache_no_cachefile(self):
        with patch('os.path.isfile', return_value=False):
            self.assertEqual(
                Cache.load_from_cache(self.cachefile,
                                      self.project_file,
                                      self.profile_dir), {}
            )
    
    def test_load_from_cache_cachefile(self):
        with patch("os.path.isfile", return_value=True):
            with patch("ads.ads.open", mock_open(read_data=self.read_data), create=True):
                with patch("ads.ads._load_spec_file", return_value=self.map):
                  self.assertEqual(
                      Cache.load_from_cache(self.cachefile,
                                            self.project_file,
                                            self.profile_dir), self.map
                  )

    def test_get_isinstance_of_service(self):
        with patch("os.path.isfile", return_value=True):
            with patch("ads.ads.open", mock_open(read_data=self.read_data), create=True):
                with patch("ads.ads._load_spec_file", return_value=self.map):
                    cache = Cache(self.project_file, self.profile_dir)
                    value = cache.get(Service("service2", self.map.get("service2")))
                    self.assertEqual(value, "/adsroot/service2/ads.yml")

    def test_get_is_string(self):
        with patch("os.path.isfile", return_value=True):
            with patch("ads.ads.open", mock_open(read_data=self.read_data), create=True):
                with patch("ads.ads._load_spec_file", return_value=self.map):
                    cache = Cache(self.project_file, self.profile_dir)
                    value = cache.get("service2")
                    self.assertEqual(value, "/adsroot/service2/ads.yml")

    def test_valid_groups_true(self):
        with patch("os.path.isfile", return_value=True):
            with patch("ads.ads.open", mock_open(read_data=self.read_data), create=True):
                with patch("ads.ads._load_spec_file", return_value=self.map):
                    cache = Cache(self.project_file, self.profile_dir)
                    self.assertEqual(cache.valid_groups(self.service_sets), True)

    def test_write_to_cache(self):
        with patch("os.path.isfile", return_value=False):
            with patch("ads.ads._load_spec_file", return_value={}):
                cache = Cache(self.project_file, self.profile_dir)
                m_open = mock_open(read_data=self.read_data)
                with patch("ads.ads.open", m_open, create=True):
                    cache.write_to_cache(self.project_file, 
                        {"random-service": "/random-service/ads.yml"}
                    )
                    self.assertEqual(cache.get("random-service"), "/random-service/ads.yml")
                    file_desc = m_open()
                    self.assertTrue(file_desc.write.called)
                      
if __name__ == '__main__':
    unittest.main()
