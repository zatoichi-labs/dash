import sys
from .development.base_component import ComponentRegistry

class Resource:
    def __init__(
            self,
            resource_type,
            external_url=None,
            relative_package_path=None,
            dev_package_path=None,
            namespace=None,
            attributes=None,
            dynamic=False
    ):
        self.resource_type = resource_type
        self.external_url = external_url
        self.attributes = attributes or {}
        self.relative_package_path = relative_package_path
        self.dev_package_path = dev_package_path
        self.namespace = namespace
        self.dynamic = dynamic


class ResourceManager:
    def __init__(self, scripts=[], stylesheets=[]):
        self._resources = []
        self._serve_scripts_locally = False
        self._serve_css_locally = False
        self._serve_dev_bundles = False

        for script in scripts:
            self.register_resource(
                resource=script,
                resource_type='js',
                resource_form='raw'
            )
        for stylesheet in stylesheets:
            self.register_resource(
                resource=stylesheet,
                resource_type='css',
                resource_form='raw'
            )

    def set_serve_css_locally(self, val):
        self._serve_css_locally = val

    def set_serve_scripts_locally(self, val):
        self._serve_scripts_locally = val

    def set_serve_dev_bundles(self, val):
        self._serve_dev_bundles = val

    def get_registered_namespaces(self):
        resources = self._get_resources(resource_type='js')
        return list(set(r.namespace for r in resources if r.namespace is not None))

    def get_registered_paths(self, namespace):
        return [
            r.relative_package_path for r in
            self._get_resources(resource_type='js', namespace=namespace)
        ]

    def register_resources(self, resources, resource_type=None, resource_form=None):
        for resource in resources:
            self.register_resource(resource, resource_type, resource_form)

    def register_resource(self, resource, resource_type=None, resource_form=None):
        # Currently, we need a resource type to process
        if resource_type not in ['js', 'css']:
            # TODO: No bare exceptions!
            raise Exception('The resource needs a type')

        if resource_form == 'raw':
            # The 'raw' resource form contains links to external assets.
            # Users will include these as `external_scripts` or `external_stylesheets`
            # arguments to the Dash constructor.
            if isinstance(resource, str):
                # The most basic resources are just a raw string.
                # e.g., resource = 'https://some.url.here.com/file_name.css'
                resource_to_register = Resource(
                    resource_type=resource_type,
                    attributes={
                        'src' if resource_type == 'js' else 'href': resource
                    }
                )
            else:
                # If not a string, the 'raw' resource form will be a dict
                # where keys are HTML attributes, values are values of those attributes
                # e.g. resource={'src': 'https://some.url.com/file_name.js, ...}
                resource_to_register = Resource(
                    resource_type=resource_type,
                    attributes=resource
                )
        elif resource_form == 'dependency':
            # The 'dependency' resource form contains resources that dependencies need.
            # These are included automatically when component suites are imported,
            # and once automatically for dash-renderer.
            # Sometimes resources are defined as long form, e.g.
            # {'external_url': ['url1', 'url2'],
            #  'relative_path': ['url1', 'url2'],
            #  'namespace': 'dash_...'}
            # rather than the record based form normally used, e.g.
            # [{'external_url': 'url1', 'relative_path': 'url1', 'namespace': 'dash_...'},
            #  {'external_url': 'url1', 'relative_path': 'url2', 'namespace': 'dash_...'}]
            # Here, we detect when we are in the former case for specialized processing.
            number_of_resources_per_key = [
                len(v)
                for v in resource.values()
                if isinstance(v, list)
            ]
            if number_of_resources_per_key and all(x > 1 for x in number_of_resources_per_key):
                # Sanity check, this should be true otherwise we cannot make sense of it.
                assert len(set(number_of_resources_per_key)) == 1
                # When reaching this point, we re-format as record based resource
                # (e.g. the latter form in the above comment) and re-register.
                number_of_resources = number_of_resources_per_key[0]
                resources = []
                for i in range(number_of_resources):
                    resources.append({
                        k: v[i] if isinstance(v, list) else v
                        for k, v in resource.items()
                    })
                self.register_resources(resources, resource_type, resource_form)
                return
            resource_to_register = Resource(resource_type=resource_type, **resource)
        self._resources.append(resource_to_register)

    def _get_resources(self, resource_type=None, namespace=None):
        resources = self._resources
        if resource_type:
            resources = [r for r in resources if r.resource_type == resource_type]
        if namespace:
            resources = [r for r in resources if r.namespace == namespace]
        return resources

    def generate_links(self):
        "Generate the header to put in HTML file, containing <link> dependencies."
        css_resources = self._get_resources(resource_type='css')
        if self._serve_css_locally:
            url_type = 'relative_package_path'
        else:
            url_type = 'external_url'
        css_resources = [
            {'href': getattr(resource, url_type)}
            if getattr(resource, url_type)
            else resource.attributes
            for resource in css_resources
            if not resource.dynamic
        ]
        return "\n".join(
            [
                '<link rel="stylesheet" {}>'.format(
                    ' '.join([
                        '{}="{}"'.format(k, v)
                        for k, v in resource.items()
                    ])
                ) for resource in css_resources
            ]
        )

    def generate_scripts(self):
        "Generate the footer to put in HTML file, containing <script> dependencies."
        js_resources = self._get_resources(resource_type='js')

        def _wrap_with_script_tag(attributes):
            # attr_tuples is a list of length two tuples.
            # First entry in each tuple is HTML attribute name
            # Second is corresponding HTML attribute value
            return '<script {}></script>'.format(
                ' '.join([
                    '{}="{}"'.format(k, v)
                    for k, v in attributes.items()
                ])
            )

        script_links = []
        for resource in js_resources:
            # We do not create a script link for dynamic resources
            if resource.dynamic:
                continue
            # Create a script tag for this resource
            if self._serve_scripts_locally:
                # If we are serving scripts locally, we have two options:
                # 1. This is a normal JS file included via assets.
                #    In this case, the resource will have 'src' defined in its attributes.
                # 2. This is a dash component suite dependency served at a Flask endpoint
                #    In this case, the resource will have a 'relative_package_path' attribute.
                if resource.relative_package_path is not None:
                    src = '{}_dash-component-suites/{}/{}?v={}&m={}'.format(
                        '',
                        resource.namespace,
                        resource.relative_package_path,
                        sys.modules[resource.namespace].__version__,
                        1
                    )
                    script_links.append(_wrap_with_script_tag({'src': src}))
                elif 'src' in resource.attributes:
                    script_links.append(_wrap_with_script_tag(resource.attributes))
        return '\n'.join(script_links)
