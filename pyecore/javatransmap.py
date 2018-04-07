import datetime

# Must be completed
# tuple is '(implem_type, use_type_as_factory, default_value)'
javaTransMap = {
    'int': (int, False, 0),
    'boolean': (bool, False, False),
    'byte': (int, False, 0),
    'short': (int, False, 0),
    'long': (int, False, 0),
    'float': (float, False, 0.0),
    'char': (str, False, ''),
    'double': (float, False, 0.0),
    'byte[]': (bytearray, True, None),
    'java.lang.Integer': (int, False, None),
    'java.lang.String': (str, False, None),
    'java.lang.Character': (str, False, None),
    'java.lang.Boolean': (bool, False, False),
    'java.lang.Short': (int, False, None),
    'java.lang.Long': (int, False, None),
    'java.lang.Float': (float, False, None),
    'java.lang.Double': (float, False, None),
    'java.lang.Class': (type, False, None),
    'java.lang.Byte': (int, False, None),
    'java.lang.Object': (object, False, None),
    'java.util.List': (list, True, None),
    'java.util.Set': (set, True, None),
    'java.util.Map': (dict, True, None),
    'java.util.Map$Entry': (dict, True, None),
    'java.util.Date': (datetime, False, None),
    'org.eclipse.emf.common.util.EList': (list, True, None),
    'org.eclipse.emf.ecore.util.FeatureMap': (dict, True, None),
    'org.eclipse.emf.ecore.util.FeatureMap$Entry': (dict, True, None)
}
