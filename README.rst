

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
    
    schema_repr = WTFormToJSONSchema().convert_form(MyForm)


TODO: To embed a JSON Schema as a form field::

    from wtforms_jsonschema.forms import JSONSchemaField
    
    #where schema is a python dictionay like schema_repr in the first exmaple
    
    class MyForm(forms.Form):
        subfield = JSONSchemaField(schema=schema)
    
    form = MyForm(data={'subfield':'<json encoded value>'})
    form.validate() #will validate the subfield entry against schema
    form['subfield'].as_widget() #will render a textarea widget with a data-schemajson attribute
