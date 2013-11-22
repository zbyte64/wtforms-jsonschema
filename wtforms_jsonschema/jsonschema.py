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
            'ux-widget': 'file-select', #not part of spec but flags behavior
        },
        'FileField': {
            'type': 'string',
            'format': 'uri',
            'ux-widget': 'file-select', #not part of spec but flags behavior
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
        'SearchField': {
            'type': 'string',
        },
        'TelField': {
            'type': 'string',
            'format': 'phone',
        },
        'EmailField': {
            'type': 'string',
            'format': 'email',
        },
        'DateTimeLocalField': {
            'type': 'string',
            'format': 'datetime',
        },
        'ColorField': {
            'type': 'string',
            'format': 'color',
        },
        #TODO min/max
        'DecimalRangeField': {
            'type': 'number',
        },
        'IntegerRangeField': {
            'type': 'integer',
        },
    }

    INPUT_TYPE_MAP = {
        'text': 'StringField',
        'checkbox': 'BooleanField',
        'color': 'ColorField',
        'tel': 'TelField',
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
        if hasattr(form, '_unbound_fields'):
            if form._unbound_fields is None:
                form = form()
            fields = [name for name, ufield in form._unbound_fields]
        else:
            fields = form._fields.keys()
        for name in fields:
            field = form._fields[name]
            json_schema['properties'][name] = \
                self.convert_formfield(name, field, json_schema)
        return json_schema


    def convert_formfield(self, name, field, json_schema):
        widget = field.widget
        target_def = {
            'title': field.label.text,
            'description': field.description,
        }
        if field.flags.required:
            target_def['required'] = True
            json_schema.setdefault('required', list())
            json_schema['required'].append(name)
        ftype = type(field).__name__
        if hasattr(self, 'convert_%s' % ftype):
            return getattr(self, 'convert_%s' % ftype)(name, field, json_schema)
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
            it = self.INPUT_TYPE_MAP.get(widget.input_type, 'StringField')
            if hasattr(self, 'convert_%s' % it):
                return getattr(self, 'convert_%s' % it)(name, field, json_schema)
            target_def.update(self.conversions[it])
        else:
            target_def['type'] = 'string'
        return target_def

    def convert_SelectField(self, name, field, json_schema):
        values = list()
        for val, label in field.choices:
            if isinstance(label, (list, tuple)):  # wonky option groups
                values.extend([x for x, y in label])
            else:
                values.append(val)

        target_def = {
            'title': field.label.text,
            'description': field.description,
            'enum': values,
            'ux-widget-choices': list(field.choices),
        }
        if field.flags.required:
            target_def['required'] = True
        return target_def

    def convert_RadioField(self, name, field, json_schema):
        target_def = {
            'title': field.label.text,
            'description': field.description,
            'enum': [x for x, y in field.choices],
            'ux-widget': 'radio',
            'ux-widget-choices': list(field.choices),
        }
        if field.flags.required:
            target_def['required'] = True
        return target_def

