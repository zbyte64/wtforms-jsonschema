from collections import OrderedDict


def pretty_name(name):
    """Converts 'first_name' to 'First name'"""
    if not name:
        return u''
    return name.replace('_', ' ').capitalize()


class WTFormToJSONSchema(object):
    DEFAULT_CONVERSIONS = {
        'URLField': {
            'type': 'string',
            'format': 'url',
        },
        'FileField': {
            'type': 'string',
            'format': 'uri',
        },
        'DateField': {
            'type': 'string',
            'format': 'date',
        },
        'DateTimeField': {
            'type': 'string',
            'format': 'datetime',
        },
        'DecimalField': {
            'type': 'number',
        },
        'IntegerField': {
            'type': 'integer',
        },
        'BooleanField': {
            'type': 'boolean',
        },
        'StringField': {
            'type': 'string',
        },
    }

    def __init__(self, conversions=None):
        self.conversions = conversions or self.DEFAULT_CONVERSIONS

    def convert_form(self, form, json_schema=None):
        if json_schema is None:
            json_schema = {
                #'title':dockit_schema._meta
                #'description'
                'type': 'object',
                'properties': OrderedDict(),
            }
        #CONSIDER: base_fields when given a class, fields for when given an instance
        for name, field in form._fields.items():
            json_schema['properties'][name] = self.convert_formfield(name, field, json_schema)
        return json_schema

    input_type_map = {
        'text': 'StringField',
        'checkbox': 'BooleanField',
    }

    def convert_formfield(self, name, field, json_schema):
        widget = field.widget
        target_def = {
            'title': field.label.text,
            'description': field.description,
        }
        if field.flags.required:
            target_def['required'] = [name]  # TODO this likely is not correct
        ftype = type(field).__name__
        params = self.conversions.get(ftype)
        if params is not None:
            target_def.update(params)
        elif ftype == 'FormField':
            target_def.update(self.convert_form(field.form_class(obj=getattr(field, '_obj', None))))
        elif ftype == 'FieldList':
            target_def['type'] = 'array'
            subfield = field.unbound_field.bind(getattr(field, '_obj', None), name)
            target_def['items'] = self.convert_formfield(name, subfield, json_schema)
        elif hasattr(widget, 'input_type'):
            it = self.input_type_map.get(widget.input_type, 'StringField')
            target_def.update(self.conversions[it])
        else:
            target_def['type'] = 'string'
        return target_def

