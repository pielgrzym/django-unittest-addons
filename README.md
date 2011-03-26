Django Test Utils
=================

Warning! 
--------

Project at very early stage.

Purpose
-------

This humble piece of code provides a helper class FormTestCase to automate django's ModelForm testing. You just need to specify the view (as if you would specify it for 'reverse' function), model form class and data. Rest of stuff - submitting, logging in and comparing is done by the class. Class can be used with ModelForms that combine fields of two models - only thing to do is to specify submodel_fields fro the assertModelEquals method.

Usage example
-------------

Special class FormTestCase for testing ModelForms. Usage is pretty straight-forward:

For MyModel, MyModelAdminForm and named-url 'create_new_mymodel' we can create a test case:

        class MyModelFormTest(FormTestCase):
            form = MyModelAdminForm
            urlname = 'create_new_mymodel'

            fixtures = [
                'mymodel.json',
            ]

            def test_form(self):
                post_data = {
                        'name' : 'Test name',
                        'slug' : 'test-slug',
                        'created': '12-03-2011'
                }
                exclude_fields = [ 'useless_id', 'somefield' ]
                self.post(post_data)
                self.assertModelEquals(post_data, exclude_fields=exclude_fields)

Above magic TestCase is capable of performing a login/logout via django client and test post data against model data inside test db. It inherits from TestCase, so usage is pretty straightforward.
