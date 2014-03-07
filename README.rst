

============
Introduction
============

wtforms-jsonschema converts WTForms into JSON Schema compatibile representations

------------
Requirements
------------

* Python 2.6 or later
* Wtforms


=====
Usage
=====

To convert a form to a JSON Schema::

    from wtforms_jsonschema.jsonschema import WTFormToJSONSchema
    from wtforms.form import Form
    from wtforms import fields
    
    class MyForm(Form):
        name = fields.StringField()
        age = fields.IntegerField()
        description = fields.StringField()
    
    schema_repr = WTFormToJSONSchema().convert_form(MyForm)
    #{'type': 'object', 'properties': OrderedDict([('name', {'type': 'string', 'description': u'', 'title': u'Name'}), ('age', {'type': 'integer', 'description': u'', 'title': u'Age'}), ('description', {'type': 'string', 'description': u'', 'title': u'Description'})])}


All wtform's fields are supported including FormField and ListField. Circular references are currently unsupported.


TODO: To embed a JSON Schema as a form field::

    from wtforms_jsonschema.forms import JSONSchemaField
    
    #where schema is a python dictionay like schema_repr in the first exmaple
    
    class MyForm(forms.Form):
        subfield = JSONSchemaField(schema=schema)
    
    form = MyForm(data={'subfield':'<json encoded value>'})
    form.validate() #will validate the subfield entry against schema
    form['subfield'].as_widget() #will render a textarea widget with a data-schemajson attribute

