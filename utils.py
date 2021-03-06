# -*- coding: utf-8 -*-
"""
FormTestCase - helper class to simplify model form test creation

class MyModelFormTest(FormTestCase):
    form = MyModelAdminForm
    urlname = 'create_new_mymodel'

    fixtures = [
        'mymodel.json',
    ]
"""
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.forms.models import ModelChoiceField
from datetime import datetime, date, time

class FormTestCaseMetaclass(type):
    def __new__(cls, name, bases, attrs):
        """Metaclass for FormTestCase"""
        form = attrs.pop('form')
        urlname = attrs.pop('urlname')
        newattrs = attrs

        if form:
            newattrs['_form'] = form
            newattrs['_form_model'] = form._meta.model

        newattrs['_default_user'] = attrs.pop('default_user', ('admin', '12345'))
        newattrs['_date_format'] = attrs.pop('date_format', '%d-%m-%Y')
        newattrs['_urlname'] = urlname

        return super(FormTestCaseMetaclass, cls).__new__(cls, name, bases, newattrs)

class FormTestCase(TestCase):
    __metaclass__ = FormTestCaseMetaclass
    form = None
    urlname = None
    default_user = None

    def setUp(self):
        #TODO: move this into less intrusive place
        from django.contrib.auth.models import User
        #TODO: make user query customizable
        admin = User.objects.get(pk=1)
        admin.set_password(self._default_user[1])
        admin.save()

    def assertModelEquals(self, data, model_instance=None, **kwargs):
        """
        exclude_fields = ['field1', 'field2', 'field3']
        submodel_fields = {
            'field1' : ['fk_pointing_to_submodel', 'submodel_field_to_check'],
            'field2' : ['fk_pointing_to_submodel', 'submodel_field_to_check'],
            ...
        }
        """
        if not model_instance:
            model_instance = self._form_model.objects.all()[0]
        exclude_fields = kwargs.get('exclude_fields', None)
        if exclude_fields:
            for field in exclude_fields:
                del data[field]

        form_instance = self._form()
        form_fields = []

        submodel_fields = kwargs.get('submodel_fields', None)
        if submodel_fields:
            for x in submodel_fields.keys():
                if data.has_key(x): # check in case exclude_fields removed the key already
                    del data[x] # we don't want to check this field twice

                fname = x
                ftype = form_instance.fields[x]
                fvalue = submodel_fields[x][1]
                fk_field = getattr(model_instance, submodel_fields[x][0])
                mvalue = getattr(fk_field, submodel_fields[x][1])

                form_fields.append((fname,ftype,fvalue,mvalue))

        form_fields += [ (x, form_instance.fields[x], data[x],
                         getattr(model_instance, x)) for x in data.keys() ]

        for fname, ftype, fvalue, mvalue in form_fields:
            if isinstance(ftype, ModelChoiceField):
                self.failUnlessEqual(fvalue, mvalue.pk)
            elif isinstance(mvalue, datetime):
                fdate = datetime.strptime(fvalue, self._date_format)
                self.failUnlessEqual(fdate, mvalue)
            #TODO: more field tests



    def post(self, data, assert_status=200, **kwargs):
        response = self.client.post(reverse(self._urlname), data)
        if assert_status:
            self.failUnlessEqual(response.status_code, assert_status)
        return response
