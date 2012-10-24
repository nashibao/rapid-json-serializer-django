# -*- coding: utf-8 -*-
# old django serialization
# from django.db import models
# from django.core.serializers import serialize as djangoserialize


# def deprecated_serialize(dic):
#     data = u'{"version":"1.0","encoding":"UTF-8",'
#     for key, val in dic.items():
#         s = ""
#         if isinstance(val, models.Model):
#             pass
#             s = djangoserialize('json', [val], ensure_ascii=False)
#         elif isinstance(val, str) or isinstance(val, unicode):
#             pass
#             s = '"' + val + '"'
#         else:
#             pass
#             s = djangoserialize('json', val, ensure_ascii=False)
#         data += '"%s":%s,' % (key, s)
#     data = re.sub(r',$', '', data)
#     data += u'}'
#     return data

import re

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.simplejson import dumps
from django.db.models.query import ValuesQuerySet
from django.db.models.query import ValuesListQuerySet
from django.db.models.query import QuerySet
from django.db.models import Model
from django.forms.models import model_to_dict

max_depth = 20


def serialize(obj, depth=0, isModel=False, nowrapper=False, option=None):
    u'replacement to django original serialization method.'
    if depth > max_depth:
        raise Exception("max_depth_error")
    ans = ''
    if isModel:
        if nowrapper:
            ans = serialize(obj, depth=depth + 1, nowrapper=nowrapper, option=option)
        else:
            ans = u'{"pk":%s, "fields":' % obj["id"]
            ans += u"%s}" % serialize(obj, depth=depth + 1, nowrapper=nowrapper, option=option)
    elif isinstance(obj, dict):
        if depth == 0:
            ans = u'{"version":"1.0","encoding":"UTF-8",'
        else:
            ans = u'{'
        for key, val in obj.items():
            s = serialize(val, depth=depth + 1, nowrapper=nowrapper, option=option)
            key = re.sub(r'_id', '', key)
            ans += u'"%s":%s, ' % (key, s)
        ans = re.sub(r', $', '', ans)
        ans += "}"
    elif isinstance(obj, (list, ValuesListQuerySet)):
        ans = u"["
        for o in obj:
            ans += u"%s, " % serialize(o, depth=depth + 1, nowrapper=nowrapper, option=option)
        ans = re.sub(r', $', '', ans)
        ans += u"]"
    elif isinstance(obj, ValuesQuerySet):
        ans = u"["
        for o in obj:
            ans += u'%s, ' % serialize(o, depth=depth + 1, isModel=True, nowrapper=nowrapper, option=option)
        ans = re.sub(r', $', '', ans)
        ans += u"]"
    elif isinstance(obj, QuerySet):
        ans = serialize([o for o in obj], depth=depth + 1, nowrapper=nowrapper, option=option)
    elif isinstance(obj, Model):
        dic = model_to_dict(obj)
        if '_external_serialize_fields' in dir(obj):
            for k, v in getattr(obj, '_external_serialize_fields')(obj=obj, option=option).items():
                dic[k] = v
        if '_global_external_serialize_fields' in dir(obj):
            for k, v in getattr(obj, '_global_external_serialize_fields')(obj=obj, option=option).items():
                dic[k] = v
        if '_exclude_serialize_fields' in dir(obj):
            for k in getattr(obj, '_exclude_serialize_fields')(obj=obj, option=option):
                if k in dic:
                    del dic[k]
        ans = serialize(dic, depth=depth + 1, isModel=True, nowrapper=nowrapper, option=option)
    else:
        ans = dumps(obj, cls=DjangoJSONEncoder)
    return ans
