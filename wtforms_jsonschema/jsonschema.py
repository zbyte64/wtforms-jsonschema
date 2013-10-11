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
            'format': 'uri',
        },
        'URIField': {
            'type': 'string',
            'format': 'uri',
        },
        'URIFileField': {
            'type': 'string',
            'format': 'uri',
            'action': 'file-select', #not part of spec but flags behavior
        },
        'FileField': {
            'type': 'string',
            'format': 'uri',
            'action': 'file-select', #not part of spec but flags behavior
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

    def __init__(self, conversions=None, include_array_item_titles=True,
            include_array_title=True):
        self.conversions = conversions or self.DEFAULT_CONVERSIONS
        self.include_array_item_titles = include_array_item_titles
        self.include_array_title = include_array_title

    def convert_form(self, form, json_schema=None):
        if json_schema is None:
            json_schema = {
                #'title':dockit_schema._meta
                #'description'
                'type': 'object',
                'properties': OrderedDict(),
            }
        #_unbound_fields preserves order, _fields does not
        for name, unbound_field in form._unbound_fields:
            field = form._fields[name]
            json_schema['properties'][name] = \
                self.convert_formfield(name, field, json_schema)
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
            if not self.include_array_title:
                target_def.pop('title')
                target_def.pop('description')
            target_def['type'] = 'array'
            subfield = field.unbound_field.bind(getattr(field, '_obj', None), name)
            target_def['items'] = self.convert_formfield(name, subfield, json_schema)
            if not self.include_array_item_titles:
                target_def['items'].pop('title')
                target_def['items'].pop('description')
        elif hasattr(widget, 'input_type'):
            it = self.input_type_map.get(widget.input_type, 'StringField')
            target_def.update(self.conversions[it])
        else:
            target_def['type'] = 'string'
        return target_def

