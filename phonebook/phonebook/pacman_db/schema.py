from django.db.backends.base.schema import BaseDatabaseSchemaEditor

from .utils import (
    is_django_1,
    is_django_2,
    is_string,
    quote_postgre
)

class DatabaseSchemaEditorMixin(object):
    def _constraint_names(self, model, column_names=None, unique=None,
                          primary_key=None, index=None, foreign_key=None,
                          check=None, type_=None):
        """Return all constraint names matching the columns and conditions."""
        if column_names is not None:
            column_names = [
                self.connection.introspection.column_name_converter(name)
                for name in column_names
            ]

        constraints = self.connection.introspection.get_constraints(model)

        result = []
        for name, infodict in constraints.items():
            if column_names is None or column_names == infodict['columns']:
                if unique is not None and infodict['unique'] != unique:
                    continue
                if primary_key is not None and \
                        infodict['primary_key'] != primary_key:
                    continue
                if index is not None and infodict['index'] != index:
                    continue
                if check is not None and infodict['check'] != check:
                    continue
                if foreign_key is not None and not infodict['foreign_key']:
                    continue
                if type_ is not None and infodict['type'] != type_:
                    continue
                result.append(name)
        return result

    def _create_index_name(self, model_or_table_name, *args, **kwargs):
        if is_django_2() and not is_string(model_or_table_name):
            model_or_table_name = model_or_table_name._meta.db_table
        return super(DatabaseSchemaEditorMixin, self)._create_index_name(
            model_or_table_name, *args, **kwargs)


class DatabaseSchemaEditor(DatabaseSchemaEditorMixin,
                           BaseDatabaseSchemaEditor):

    sql_alter_column_type = ("ALTER COLUMN %(column)s "
                             "TYPE %(type)s USING %(column)s::%(type)s")

    sql_create_sequence = "CREATE SEQUENCE %(sequence)s"
    sql_delete_sequence = "DROP SEQUENCE IF EXISTS %(sequence)s CASCADE"
    sql_set_sequence_max = ("SELECT setval('%(sequence)s', "
                            "MAX(%(column)s)) FROM %(table)s")

    sql_create_index = ("CREATE INDEX %(name)s ON "
                        "%(table)s%(using)s (%(columns)s)%(extra)s")
    sql_create_varchar_index = ("CREATE INDEX %(name)s ON %(table)s "
                                "(%(columns)s varchar_pattern_ops)%(extra)s")
    sql_create_text_index = ("CREATE INDEX %(name)s ON %(table)s "
                             "(%(columns)s text_pattern_ops)%(extra)s")
    sql_delete_index = "DROP INDEX IF EXISTS %(name)s"

    # Setting the constraint to IMMEDIATE runs any deferred checks to allow
    # dropping it in the same transaction.
    sql_delete_fk = ("SET CONSTRAINTS %(name)s IMMEDIATE; "
                     "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s")

    sql_delete_procedure = 'DROP FUNCTION %(procedure)s(%(param_types)s)'

    def quote_value(self, value):
        return quote_postgre(value)

    def _field_indexes_sql(self, model, field):
        output = super(DatabaseSchemaEditor, self)._field_indexes_sql(
            model, field)
        like_index_statement = self._create_like_index_sql(model, field)
        if like_index_statement is not None:
            output.append(like_index_statement)
        return output

    def _create_like_index_sql(self, model, field):
        """
        Return the statement to create an index with varchar operator pattern
        when the column type is 'varchar' or 'text', otherwise return None.
        """
        db_type = field.db_type(connection=self.connection)
        if db_type is not None and (field.db_index or field.unique):
            # Fields with database column types of `varchar` and `text` need
            # a second index that specifies their operator class, which is
            # needed when performing correct LIKE queries outside the
            # C locale. See #12234.
            #
            # The same doesn't apply to array fields such as varchar[size]
            # and text[size], so skip them.
            if '[' in db_type:
                return None
            if db_type.startswith('varchar'):
                return self._create_index_sql(
                    model,
                    [field],
                    suffix='_like',
                    sql=self.sql_create_varchar_index)
            elif db_type.startswith('text'):
                return self._create_index_sql(
                    model,
                    [field],
                    suffix='_like',
                    sql=self.sql_create_text_index)
        return None

    def _alter_column_type_sql(
            self, model_or_table, old_field, new_field, new_type):
        """Make ALTER TYPE with SERIAL make sense."""
        if is_django_2() and is_string(model_or_table):
            model_or_table = model_or_table._meta.db_table
            table = model_or_table._meta.db_table
        else:
            table = model_or_table
        if new_type.lower() in ("serial", "bigserial"):
            column = new_field.column
            sequence_name = "%s_%s_seq" % (table, column)
            col_type = "integer" if new_type.lower() == "serial" else "bigint"
            return (
                (
                    self.sql_alter_column_type % {
                        "column": self.quote_name(column),
                        "type": col_type,
                    },
                    [],
                ),
                [
                    (
                        self.sql_delete_sequence % {
                            "sequence": self.quote_name(sequence_name),
                        },
                        [],
                    ),
                    (
                        self.sql_create_sequence % {
                            "sequence": self.quote_name(sequence_name),
                        },
                        [],
                    ),
                    (
                        self.sql_alter_column % {
                            "table": self.quote_name(table),
                            "changes": self.sql_alter_column_default % {
                                "column": self.quote_name(column),
                                "default": "nextval('%s')" % self.quote_name(
                                    sequence_name),
                            }
                        },
                        [],
                    ),
                    (
                        self.sql_set_sequence_max % {
                            "table": self.quote_name(table),
                            "column": self.quote_name(column),
                            "sequence": self.quote_name(sequence_name),
                        },
                        [],
                    ),
                ],
            )
        else:
            return super(DatabaseSchemaEditor, self)._alter_column_type_sql(
                model_or_table, old_field, new_field, new_type)

    def _alter_field(self, model, old_field, new_field, old_type, new_type,
                     old_db_params, new_db_params, strict=False):
        if is_django_1():
            return self._alter_field_django1(
                model, old_field, new_field, old_type, new_type,
                old_db_params, new_db_params, strict=False)
        else:
            return self._alter_field_django2(
                model, old_field, new_field, old_type, new_type,
                old_db_params, new_db_params, strict=False)

    def _alter_field_django1(self, model, old_field, new_field,
                             old_type, new_type,
                             old_db_params, new_db_params, strict=False):
        super(DatabaseSchemaEditor, self)._alter_field(
            model, old_field, new_field, old_type, new_type, old_db_params,
            new_db_params, strict,
        )
        # Added an index? Create any PostgreSQL-specific indexes.
        if ((not (old_field.db_index or old_field.unique)
             and new_field.db_index) or
                (not old_field.unique and new_field.unique)):
            like_index_statement = self._create_like_index_sql(
                model, new_field)
            if like_index_statement is not None:
                self.execute(like_index_statement)

        # Removed an index? Drop any PostgreSQL-specific indexes.
        if (old_field.unique and
                not (new_field.db_index or new_field.unique)):
            index_to_remove = self._create_index_name(
                model, [old_field.column], suffix='_like')
            index_names = self._constraint_names(
                model, [old_field.column], index=True)
            for index_name in index_names:
                if index_name == index_to_remove:
                    self.execute(self._delete_constraint_sql(
                        self.sql_delete_index, model, index_name))

    def _alter_field_django2(self, model, old_field, new_field,
                             old_type, new_type,
                             old_db_params, new_db_params, strict=False):
        # Drop indexes on varchar/text/citext columns
        # that are changing to a
        # different type.
        if (old_field.db_index or old_field.unique) and (
            (old_type.startswith('varchar') and not
                new_type.startswith('varchar')) or
            (old_type.startswith('text') and
                not new_type.startswith('text')) or
            (old_type.startswith('citext') and
                not new_type.startswith('citext'))
        ):
            index_name = self._create_index_name(
                model, [old_field.column], suffix='_like')
            self.execute(self._delete_constraint_sql(
                self.sql_delete_index, model, index_name))

        super(DatabaseSchemaEditor, self)._alter_field(
            model, old_field, new_field, old_type, new_type, old_db_params,
            new_db_params, strict,
        )
        # Added an index? Create any PostgreSQL-specific indexes.
        if ((not (old_field.db_index or old_field.unique)
             and new_field.db_index) or
                (not old_field.unique and new_field.unique)):
            like_index_statement = self._create_like_index_sql(
                model, new_field)
            if like_index_statement is not None:
                self.execute(like_index_statement)

        # Removed an index? Drop any PostgreSQL-specific indexes.
        if (old_field.unique and
                not (new_field.db_index or new_field.unique)):
            index_to_remove = self._create_index_name(
                model, [old_field.column], suffix='_like')
            self.execute(self._delete_constraint_sql(
                self.sql_delete_index, model, index_to_remove))