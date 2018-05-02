import logging

from sqlalchemy.exc import NoSuchTableError
import migrate
from migrate.versioning import schemadiff, genmodel
log = logging.getLogger(__name__)
import ckan.model
from sqlalchemy import Table, Column, Boolean, UnicodeText, ForeignKey
from sqlalchemy.orm import mapper

table_name = 'user_ext'

class UserExt(object):
    @classmethod
    def get(cls, user_id):
        query = ckan.model.meta.Session.query(cls).autoflush(False)
        query = query.filter(cls.user_id == user_id)
        return query.first()

    @classmethod
    def get_cols(cls, user_id, *cols):
        query = ckan.model.meta.Session.query(cls).autoflush(False)
        query.add_columns(*cols)
        query = query.filter(cls.user_id == user_id)
        return query.first()

    @classmethod
    def set_cols(cls, user_id, **cols):
        obj = cls()
        setattr(obj, 'user_id', user_id)
        for c, v in cols.items():
            setattr(obj, c, v)
        ckan.model.meta.Session.add(obj)
        ckan.model.meta.Session.commit()


def get_table_diff(table):
    metadata = table.metadata
    all_tables = set(metadata.tables.keys())
    all_tables.remove(table.name)
    d = schemadiff.getDiffOfModelAgainstDatabase(metadata, metadata.bind, excludeTables=all_tables)
    return d

def strip_diff(diff):
    #ensure we are only getting
    diff.tables_missing_from_A = []
    diff.tables_missing_from_B = []
    if diff.tables_different:
        if table_name in diff.tables_different.keys():
            diff.tables_different = {table_name: diff.tables_different[table_name]}
        else:
            diff.tables_different = {}
    return diff

def make_table(metadata, *cols):
    primary_col = Column('user_id', UnicodeText, ForeignKey("user.id"),
                         primary_key=True)
    auto_load = False
    create = False
    try:
        #test table exists?
        _ = Table(table_name, metadata,
                  primary_col, autoload=True)
        auto_load = True
    except NoSuchTableError:
        # don't autoload existing table
        create = True

    user_ext = Table(table_name, metadata,
                     primary_col, *cols,
                     extend_existing=True,
                     autoload=auto_load)
    if create:
        metadata.create_all(bind=metadata.bind, tables=[user_ext])
    else:
        d = strip_diff(get_table_diff(user_ext))
        if d:
            g = genmodel.ModelGenerator(d, metadata.bind)
            g.runB2A()
    mapper(UserExt, user_ext)
    return user_ext

def create_or_extend_table(*cols):
    if ckan.model.user_table.exists():
        user_ext = make_table(ckan.model.meta.metadata, *cols)
        return user_ext
    else:
        return None

def register_additional_class(table, new_cls):
    assert issubclass(new_cls, UserExt)
    mapper(new_cls, table, inherits=UserExt)

