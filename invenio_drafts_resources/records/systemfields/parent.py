# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Drafts-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Parent record system field."""

from invenio_db import db
from invenio_records.systemfields import RelatedModelField
from sqlalchemy.exc import IntegrityError


class ParentField(RelatedModelField):
    """Parent record field."""

    def __init__(self, parent_record_cls, key=None, create=False,
                 soft_delete=True, hard_delete=True):
        """Initialize the parent field."""
        # Note, self._parent_record_cls == self._model, we duplicate it for
        # clarity of naming.
        self._parent_record_cls = parent_record_cls
        self._soft_delete = soft_delete
        self._hard_delete = hard_delete
        self._create = create
        super().__init__(
            parent_record_cls,
            key=key,
            required=True,
            dump=self.dump_parent,
            load=self.load_parent,
        )

    def create(self, record):
        """Method to create the parent record for the record."""
        # Create a parent record
        parent = self._parent_record_cls.create({})
        # This bumps revision id to 2 for the first record. Commit needed
        # because of the system fields defined on the parent record (e.g. pid).
        parent.commit()

        # Set using the __set__() method
        setattr(record, self.attr_name, parent)

        return parent

    def delete(self, record, force=False):
        """Method to delete the parent record.

        The parent record will only be hard deleted if this is the last
        record/draft with links to it.
        """
        # A *record* is configured to never delete the parent
        # automatically.
        # A *draft* is configured to delete the parent on hard delete but not
        # soft delete.
        #
        # A draft may be hard-deleted in two cases: 1) a new record 2) a new
        # record version. In the case 1, only a draft and the parent record
        # exists. In case 2, one or more drafts and records may exists with a
        # foreign key to the parent record.
        #
        # The logic implemented here, thus on a hard delete tries to delete the
        # the parent record and relies on the database integrity constraints
        # to prevent the parent record from being deleted in case more
        # drafts/records.
        parent = getattr(record, self.attr_name)
        if parent:
            if force and self._hard_delete:
                try:
                    with db.session.begin_nested():
                        parent.delete(force=True)
                except IntegrityError:
                    # It's ok - the draft/record linking to this parent is not
                    # the last one.
                    pass
            elif not force and self._soft_delete:
                parent.delete(force=False)

    #
    # Life-cycle hooks
    #
    def pre_create(self, record):
        """Called before a record is created (but after being initialized)."""
        if self._create:
            self.create(record)

    def post_delete(self, record, force=False):
        """Called after a record is deleted."""
        if self._hard_delete or self._soft_delete:
            self.delete(record, force=force)

    def pre_dump(self, record, data, dumper=None):
        """Called before a record is dumped."""
        parent = getattr(record, self.attr_name)
        # Use the default dumper for the parent (since the records/drafts
        # dumpers won't work on a parent)
        if parent:
            data[self.attr_name] = parent.dumps(dumper=None)

    def post_load(self, record, data, loader=None):
        """Called after a record was loaded."""
        parent_dump = record.pop(self.attr_name, None)
        if parent_dump:
            parent = self._parent_record_cls.loads(parent_dump, loader=loader)
            setattr(record, self.attr_name, parent)

    #
    # Helpers
    #
    @staticmethod
    def load_parent(field, record):
        """Serializer the object into a record."""
        if record.model.parent_id:
            return field._parent_record_cls.get_record(record.model.parent_id)
        return None

    @staticmethod
    def dump_parent(field, record, parent_record):
        """Set the object."""
        record.model.parent_id = parent_record.id
