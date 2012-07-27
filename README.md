rapid-json-serializer-django
============================

replacement for heavy serialization package in django.

what this lib does..

1. performance improvement
default serialization in django is too slow.

2. serialize additional fields
if you would like to add non-default fields in serialization(in most case, functions are example.), you can add '''_external_serialize_fields'''func that return a dictionary.

enjoy!