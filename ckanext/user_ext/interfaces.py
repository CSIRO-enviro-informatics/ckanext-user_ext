# encoding: utf-8

import ckan.plugins.interfaces as interfaces

class IUserExt(interfaces.Interface):
    '''This is a dummy Interface to allow us to find all '''

class IUserExtension(interfaces.Interface):
    '''Allow modifying UserExt db'''

    def get_table_columns(self):
        '''Returns the Columns we want to put in the table'''
        return None

    def get_model_classes(self):
        '''Returns the Classes for the models representing the tables'''
