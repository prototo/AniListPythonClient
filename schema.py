import yaml

class Schema:
    base_path = ''
    schema = {}

    def __init__(self, config='schema.yml'):
        with open(config) as f:
            self.schema = yaml.load(f.read())
        self.base_path = self.schema.get('basepath', '')

    def __getattr__(self, item):
        return self.get_schema(item)

    def get_schema(self, signature):
        parts = signature.lower().split('_')
        path = self.base_path
        schema = self.schema
        part = None

        while True:
            if not schema:
                return False

            # add any additional path sections
            if 'path' in schema:
                path = '/'.join((path, schema.get('path')))

            # fall into routes blocks
            if 'routes' in schema:
                schema = schema.get('routes')

            if not len(parts):
                break

            # get the next block or exit the loop
            part = parts.pop(0)
            schema = schema.get(part, None)

        schema['path'] = path
        return schema

