from unittest import TestCase
from dash.resource_manager import Resource, ResourceManager


class Tests(TestCase):
    def test_resource_manager_initializes_empty(self):
        rm = ResourceManager()
        assert rm._resources == []

    def test_resource_manager_initializes_stylesheets_single_url(self):
        single_url_ss = 'https://hello.world.com/file.css'
        external_stylesheets = [single_url_ss]
        rm = ResourceManager(stylesheets=external_stylesheets)
        resource = rm._resources[0]
        assert resource.external_url == single_url_ss
        assert resource.resource_type == 'css'

    def test_resource_manager_initializes_stylesheets_attributes_dict(self):
        attributes_ss = {
            'href': 'https://hello.world.com/file.css',
            'variable1': 'hello',
            'variable2': 'world'
        }
        external_stylesheets = [attributes_ss]
        rm = ResourceManager(stylesheets=external_stylesheets)
        resource = rm._resources[0]
        assert resource.attributes == attributes_ss
        assert resource.resource_type == 'css'

    def test_resource_manager_initializes_scripts_single_url(self):
        single_url_js = 'https://hello.world.com/file.js'
        external_scripts = [single_url_js]
        rm = ResourceManager(scripts=external_scripts)
        resource = rm._resources[0]
        assert resource.external_url == single_url_js
        assert resource.resource_type == 'js'

    def test_resource_manager_initializes_scripts_attributes_dict(self):
        attributes_js = {
            'src': 'https://hello.world.com/file.js',
            'variable1': 'hello',
            'variable2': 'world'
        }
        external_scripts = [attributes_js]
        rm = ResourceManager(scripts=external_scripts)
        resource = rm._resources[0]
        assert resource.attributes == attributes_js
        assert resource.resource_type == 'js'

    def test_resource_manager_can_add_js_dependencies(self):
        js_dist = [
            {
                'relative_package_path': 'fake.min.js',
                'dev_package_path': 'fake.dev.js',
                'external_url': 'https://fake.external.url/hello.js',
                'namespace': 'dash_whatever'
            }
        ]
        rm = ResourceManager()
        for dep in js_dist:
            rm.register_resource(dep, resource_type='js', resource_form='dependency')
        resource = rm._resources[0]
        assert resource.__dict__ == {
            'dynamic': False,
            'namespace': 'dash_whatever',
            'dev_package_path': 'fake.dev.js',
            'attributes': {},
            'relative_package_path': 'fake.min.js',
            'resource_type': 'js',
            'external_url': 'https://fake.external.url/hello.js'
        }

    def test_resource_manager_can_add_css_dependencies(self):
        css_dist = [
            {
                'relative_package_path': 'fake.min.css',
                'dev_package_path': 'fake.dev.css',
                'external_url': 'https://fake.external.url/hello.css',
                'namespace': 'dash_whatever'
            }
        ]
        rm = ResourceManager()
        for dep in css_dist:
            rm.register_resource(dep, resource_type='css', resource_form='dependency')
        resource = rm._resources[0]
        assert resource.__dict__ == {
            'dynamic': False,
            'namespace': 'dash_whatever',
            'dev_package_path': 'fake.dev.css',
            'attributes': {},
            'relative_package_path': 'fake.min.css',
            'resource_type': 'css',
            'external_url': 'https://fake.external.url/hello.css'
        }

    def test_resource_manager_can_add_css_dependencies(self):
        css_dist = [
            {
                'relative_package_path': 'fake.min.css',
                'dev_package_path': 'fake.dev.css',
                'external_url': 'https://fake.external.url/hello.css',
                'namespace': 'dash_whatever'
            }
        ]
        rm = ResourceManager()
        for dep in css_dist:
            rm.register_resource(dep, resource_type='css', resource_form='dependency')
        resource = rm._resources[0]
        assert resource.__dict__ == {
            'dynamic': False,
            'namespace': 'dash_whatever',
            'dev_package_path': 'fake.dev.css',
            'attributes': {},
            'relative_package_path': 'fake.min.css',
            'resource_type': 'css',
            'external_url': 'https://fake.external.url/hello.css'
        }