from datetime import datetime

from flask import g
from flask.ext.mongoengine import Document
from mongoengine import StringField, ListField, ObjectIdField, DateTimeField, \
    GeoPointField

from myhoard.apps.media.models import Media


class Item(Document):
    name = StringField(min_length=3, max_length=50, required=True)
    description = StringField(max_length=250, default='')
    location = GeoPointField()
    created_date = DateTimeField(default=datetime.now)
    modified_date = DateTimeField(default=datetime.now)
    media = ListField(ObjectIdField())
    collection = ObjectIdField(required=True)
    owner = ObjectIdField()

    def __repr__(self):
        return '<Item {}>'.format(self.name)

    @classmethod
    def create_item(cls, **kwargs):
        item = cls(**kwargs)
        item.id = None
        item.owner = g.user
        item.created_date = None
        item.modified_date = None

        if 'location' in item:
            item.location = (item.location.get('lat'), item.location.get('lng'))

        item.save()

        Media.create_item_media(item)

        return item

    @classmethod
    def update_item(cls, item_id, **kwargs):
        item = cls.objects.get_or_404(id=item_id)
        update_item = cls(**kwargs)
        update_item.id = item.id
        update_item.created_date = item.created_date
        update_item.modified_date = None

        Media.update_item_media(item, update_item)

        return update_item.save()

    @classmethod
    def delete_item(cls, item_id):
        item = cls.objects.get_or_404(id=item_id)

        Media.delete_item_media(item)

        return item.delete()

    @classmethod
    def delete_collection_items(cls, collection):
        for item in cls.objects(collection=collection.id):
            Media.delete_item_media(item)

            item.delete()