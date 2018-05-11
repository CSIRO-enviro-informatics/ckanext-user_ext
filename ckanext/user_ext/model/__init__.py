import logging

log = logging.getLogger(__name__)
import ckan.model
from sqlalchemy import Table, Column, Boolean, UnicodeText, ForeignKey
from sqlalchemy.orm import mapper, class_mapper
from sqlalchemy.exc import NoSuchTableError, InvalidRequestError
from sqlalchemy.orm.exc import UnmappedClassError
import migrate
from migrate.versioning import schemadiff, genmodel

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
    # ensure we are only getting the diff from _our_ table.
    diff.tables_missing_from_A = []
    diff.tables_missing_from_B = []
    if diff.tables_different:
        if table_name in diff.tables_different.keys():
            diff.tables_different =\
                {table_name: diff.tables_different[table_name]}
        else:
            diff.tables_different = {}
    return diff


def make_table(metadata, *cols):
    primary_col = Column('user_id', UnicodeText, ForeignKey("user.id"),
                         primary_key=True)
    auto_load = False
    create = False
    extend = False
    try:
        # test table exists?
        # setting keep_existing to False here causes the second exception
        # to throw, indicating that the table is already in the metadata.
        _ = Table(table_name, metadata, primary_col,
                  autoload=True, keep_existing=False)
        auto_load = True
        extend = True
    except NoSuchTableError:
        # don't autoload existing table
        # don't extend existing table
        create = True
    except InvalidRequestError:
        # don't create new table
        auto_load = True
        extend = True
    except Exception as e:
        log.error(str(e))
        raise e

    try:
        user_ext = Table(table_name, metadata,
                         primary_col, *cols,
                         extend_existing=extend,
                         mustexist=(not create),
                         autoload=auto_load)
    except Exception as e:
        log.error(str(e))
        raise e

    if create:
        metadata.create_all(bind=metadata.bind, tables=[user_ext])
    else:
        d = strip_diff(get_table_diff(user_ext))
        if d:
            g = genmodel.ModelGenerator(d, metadata.bind)
            g.runB2A()

    try:
        _map = class_mapper(UserExt)
        assert _map.class_ == UserExt
        assert _map.local_table is not None
        assert _map.local_table.name == table_name
    except UnmappedClassError:
        _map = mapper(UserExt, user_ext)
    except AssertionError as e:
        log.error(
            "New mapping on UserExt didn't match existing mapping")
        log.error(str(e))
    return user_ext


def create_or_extend_table(*cols):
    if ckan.model.user_table.exists():
        user_ext = make_table(ckan.model.meta.metadata, *cols)
        return user_ext
    else:
        return None


def register_additional_class(table, new_cls):
    assert new_cls != UserExt
    assert issubclass(new_cls, UserExt)

    try:
        _map = class_mapper(new_cls)
        assert _map.class_ == new_cls
        assert _map.local_table is not None
        assert _map.local_table.name == table.name
        assert _map.inherits
        try:
            i_class = _map.inherits.class_
        except AttributeError:
            i_class = _map.inherits
        assert i_class == UserExt
    except UnmappedClassError:
        _map = mapper(new_cls, table, inherits=UserExt)
    except AssertionError as e:
        log.error(
            "New mapping on existing class didn't match existing mapping")
        log.error(str(e))

