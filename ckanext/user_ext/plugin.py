import logging
from functools import partial

from sqlalchemy import Column
from ckan.plugins import implements, SingletonPlugin, PluginImplementations
from ckan.plugins import IConfigurable, IConfigurer
import ckan.plugins.toolkit as toolkit
from interfaces import IUserExt, IUserExtension
from model import create_or_extend_table, register_additional_class

log = logging.getLogger(__name__)


def get_current_user_id():
    c = toolkit.c
    try:
        user_obj = c.userobj
        user_id = user_obj.id
        return user_id
    except (TypeError, AttributeError):
        return None


class UserExtPlugin(SingletonPlugin):
    implements(IConfigurable, inherit=True)
    implements(IConfigurer)
    implements(IUserExt)

    def __new__(cls, *args, **kwargs):
        iuserext_ext = PluginImplementations(IUserExt)
        iuserext_ext = iuserext_ext.extensions()

        if iuserext_ext and iuserext_ext[0].__class__ != cls:
            msg = ('The "UserExt" plugin must be the first IUserExt '
                   'plugin loaded. Change the order it is loaded in '
                   '"ckan.plugins" in your CKAN .ini file and try again.')
            raise RuntimeError(msg)

        return super(cls, cls).__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.table = None
        self.configured_cols = None

    #Configurer
    def update_config(self, config):
        pass


    #Configurable
    def configure(self, config):
        iuserextensions = PluginImplementations(IUserExtension)
        iuserextensions = iuserextensions.extensions()
        cols = []
        these_configured_cols = set()
        for ext in iuserextensions:
            ext_class = ext.__class__
            new_cols = ext.get_table_columns()
            if new_cols is None or len(new_cols) < 1:
                continue
            for nc in new_cols:
                assert isinstance(nc, Column)
                col_name = nc.name
                col_type = nc.type
                col_c_type = col_type.__class__ if col_type else None
                these_configured_cols.add((ext_class, col_name, col_c_type))
                if nc.primary_key:
                    raise RuntimeError(
                        "Column {} cannot be a primary key.".format(col_name))
                if nc.system:
                    raise RuntimeError(
                        "Column {} cannot be a system col.".format(col_name))
                cols.append(nc)
        if self.configured_cols and \
            len(these_configured_cols.difference(self.configured_cols)) == 0:
            # we've configured already, and cols are still the same.
            return
        self.configured_cols = these_configured_cols
        try:
            self.table = create_or_extend_table(*cols)
        except Exception, e:
            log.error(str(e))
            raise e
        if self.table is not None:
            reg = partial(register_additional_class, self.table)
            for ext in iuserextensions:
                new_cls = ext.get_model_classes()
                if new_cls is None or len(new_cls) < 1:
                    continue
                for c in new_cls:
                    reg(c)
