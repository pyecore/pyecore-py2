====================================================================
PyEcore: A Pythonic Implementation of the Eclipse Modeling Framework
====================================================================

|pypi-version| |master-build| |coverage| |license|

.. |master-build| image:: https://travis-ci.org/pyecore/pyecore-py2.svg?branch=master
    :target: https://travis-ci.org/pyecore/pyecore-py2

.. |develop-build| image:: https://travis-ci.org/pyecore/pyecore-py2.svg?branch=develop
    :target: https://travis-ci.org/pyecore/pyecore-py2

.. |pypi-version| image:: https://badge.fury.io/py/pyecore-py2.svg
    :target: https://badge.fury.io/py/pyecore-py2

.. |coverage| image:: https://coveralls.io/repos/github/pyecore/pyecore-py2/badge.svg?branch=master
    :target: https://coveralls.io/github/pyecore/pyecore-py2?branch=master

.. |license| image:: https://img.shields.io/badge/license-New%20BSD-blue.svg
    :target: https://raw.githubusercontent.com/pyecore/pyecore-py2/master/LICENSE

PyEcore is a "Pythonic?" (sounds pretentious) implementation of EMF/Ecore for
Python 2.7 (backport of the `PyEcore for Python 3
<https://github.com/pyecore/pyecore>`_  version). It's purpose is to handle
model/metamodels in Python almost the same way the Java version does.

However, PyEcore enables you to use a simple ``instance.attribute`` notation
instead of ``instance.setAttribute(...)/getAttribute(...)`` for the Java
version. To achieve this, PyEcore relies on reflection (a lot).

Let see by yourself how it works on a very simple metamodel created on
the fly (dynamic metamodel):

.. code-block:: python

    >>> from pyecore.ecore import EClass, EAttribute, EString, EObject
    >>> A = EClass('A')  # We create metaclass named 'A'
    >>> A.eStructuralFeatures.append(EAttribute('myname', EString, default_value='new_name')) # We add a name attribute to the A metaclass
    >>> a1 = A()  # We create an instance
    >>> a1.myname
    'new_name'
    >>> a1.myname = 'a_instance'
    >>> a1.myname
    'a_instance'
    >>> isinstance(a1, EObject)
    True

PyEcore also support introspection and the EMF reflexive API using basic Python
reflexive features:

.. code-block:: python

    >>> a1.eClass # some introspection
    <EClass name="A">
    >>> a1.eClass.eClass
    <EClass name="EClass">
    >>> a1.eClass.eClass is a1.eClass.eClass.eClass
    True
    >>> a1.eClass.eStructuralFeatures
    EOrderedSet([<EStructuralFeature myname: EString(str)>])
    >>> a1.eClass.eStructuralFeatures[0].name
    'myname'
    >>> a1.eClass.eStructuralFeatures[0].eClass
    <EClass name="EAttribute">
    >>> a1.__getattribute__('myname')
    'a_instance'
    >>> a1.__setattr__('myname', 'reflexive')
    >>> a1.__getattribute__('myname')
    'reflexive'
    >>> a1.eSet('myname', 'newname')
    >>> a1.eGet('myname')
    'newname'

Runtime type checking is also performed (regarding what you expressed in your)
metamodel:

.. code-block:: python

    >>> a1.myname = 1
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File ".../pyecore/ecore.py", line 66, in setattr
            raise BadValueError(got=value, expected=estruct.eType)
    pyecore.ecore.BadValueError: Expected type EString(str), but got type int with value 1 instead


PyEcore does support dynamic metamodel and static ones (see details in next
sections).

*The project slowly grows and it still requires more love.*

Installation
============

PyEcore is available on ``pypi``, you can simply install it using ``pip``:

.. code-block:: bash

    $ pip install pyecore

The installation can also be performed manually (better in a virtualenv):

.. code-block:: bash

    $ python setup.py install


.. contents:: :depth: 2


Dynamic Metamodels
==================

Dynamic metamodels reflects the ability to create metamodels "on-the-fly". You
can create metaclass hierarchie, add ``EAttribute`` and ``EReference``.

In order to create a new metaclass, you need to create an ``EClass`` instance:

.. code-block:: python

    >>> import pyecore.ecore as Ecore
    >>> MyMetaclass = Ecore.EClass('MyMetaclass')

You can then create instances of your metaclass:

.. code-block:: python

    >>> instance1 = MyMetaclass()
    >>> instance2 = MyMetaclass()
    >>> assert instance1 is not instance2

From the created instances, we can go back to the metaclasses:

.. code-block:: python

    >>> instance1.eClass
    <EClass name="MyMetaclass">

Then, we can add metaproperties to the freshly created metaclass:

.. code-block:: python

    >>> instance1.eClass.eAttributes
    []
    >>> MyMetaclass.eStructuralFeatures.append(Ecore.EAttribute('name', Ecore.EString))  # We add a 'name' which is a string
    >>> instance1.eClass.eAttributes  # Is there a new feature?
    [<pyecore.ecore.EAttribute object at 0x7f7da72ba940>]  # Yep, the new feature is here!
    >>> str(instance1.name)  # There is a default value for the new attribute
    'None'
    >>> instance1.name = 'mystuff'
    >>> instance1.name
    'mystuff'
    >>> # As the feature exists in the metaclass, the name of the feature can be used in the constructor
    >>> instance3 = MyMetaclass(name='myname')
    >>> instance3.name
    'myname'

We can also create a new metaclass ``B`` and a new meta-references towards
``B``:

.. code-block:: python

    >>> B = Ecore.EClass('B')
    >>> MyMetaclass.eStructuralFeatures.append(Ecore.EReference('toB', B, containment=True))
    >>> b1 = B()
    >>> instance1.toB = b1
    >>> instance1.toB
    <pyecore.ecore.B object at 0x7f7da70531d0>
    >>> b1.eContainer() is instance1   # because 'toB' is a containment reference
    True

Opposite and 'collection' meta-references are also managed:

.. code-block:: python

    >>> C = Ecore.EClass('C')
    >>> C.eStructuralFeatures.append(Ecore.EReference('toMy', MyMetaclass))
    >>> MyMetaclass.eStructuralFeatures.append(Ecore.EReference('toCs', C, upper=-1, eOpposite=C.eStructuralFeatures[0]))
    >>> instance1.toCs
    []
    >>> c1 = C()
    >>> c1.toMy = instance1
    >>> instance1.toCs  # 'toCs' should contain 'c1' because 'toMy' is opposite relation of 'toCs'
    [<pyecore.ecore.C object at 0x7f7da7053390>]

Explore Dynamic metamodel/model objects
---------------------------------------

It is possible, when you are handling an object in the Python console, to ask
for all the meta-attributes/meta-references and meta-operations that can
be called on it using ``dir()`` on, either a dynamic metamodel object or a
model instance. This allows you to quickly experiment and find the information
you are looking for:

.. code-block:: python

    >>> A = EClass('A')
    >>> dir(A)
    ['abstract',
     'delete',
     'eAllContents',
     'eAllOperations',
     'eAllReferences',
     'eAllStructuralFeatures',
     'eAllSuperTypes',
     'eAnnotations',
     'eAttributes',
     'eContainer',
     # ... there is many others
     'findEOperation',
     'findEStructuralFeature',
     'getEAnnotation',
     'instanceClassName',
     'interface',
     'name']
    >>> a = A()
    >>> dir(a)
    []
    >>> A.eStructuralFeatures.append(EAttribute('myname', EString))
    >>> dir(a)
    ['myname']


Enhance the Dynamic metamodel
-----------------------------

Even if you define or use a dynamic metamodel, you can add dedicated methods
(e.g: ``__repr__``) to the equivalent Python class. Each ``EClass`` instance is
linked to a Python class which can be reached using the ``python_class`` field:

.. code-block:: python

    >>> A = EClass('A')
    >>> A.python_class
    pyecore.ecore.A

You can directly add new "non-metamodel" related method to this class:

.. code-block:: python

    >>> a = A()
    >>> a
    <pyecore.ecore.A at 0x7f4f0839b7b8>
    >>> A.python_class.__repr__ = lambda self: 'My repr for real'
    >>> a
    My repr for real


Static Metamodels
=================

The static definition of a metamodel using PyEcore mostly relies on the
classical classes definitions in Python. Each Python class is linked to an
``EClass`` instance and has a special metaclass. The static code for metamodel
also provides a model layer and the ability to easily refer/navigate inside the
defined meta-layer.

.. code-block:: python

    $ ls library
    __init__.py library.py

    $ cat library/library.py
    # ... stuffs here
    class Writer(EObject):
        __metaclass__ = MetaEClass
        name = EAttribute(eType=EString)
        books = EReference(upper=-1)

        def __init__(self, name=None, books=None, **kwargs):
            if kwargs:
                raise AttributeError('unexpected arguments: {}'.format(kwargs))

            super().__init__()
            if name is not None:
                self.name = name
            if books:
                self.books.extend(books)
    # ... Other stuffs here

    $ python
    ...
    >>> import library
    >>> # we can create elements and handle the model level
    >>> smith = library.Writer(name='smith')
    >>> book1 = library.Book(title='Ye Old Book1')
    >>> book1.pages = 100
    >>> smith.books.append(book1)
    >>> assert book1 in smith.books
    >>> assert smith in book1.authors
    >>> # ...
    >>> # We can also navigate the meta-level
    >>> import pyecore.ecore as Ecore  # We import the Ecore metamodel only for tests
    >>> assert isinstance(library.Book.authors, Ecore.EReference)
    >>> library.Book.authors.upperBound
    -1
    >>> assert isinstance(library.Writer.name, Ecore.EAttribute)


There is two main ways of creating static ``EClass`` with PyEcore. The first
one relies on automatic code generation while the second one uses manual
definition.

The automatic code generator defines a Python package hierarchie instead of
only a Python module. This allows more freedom for dedicated operations and
references between packages.

How to Generate the Static Metamodel Code
-----------------------------------------

The static code is generated from a ``.ecore`` where your metamodel is defined
(the EMF ``.genmodel`` files are not yet supported (probably in future version).

There is currently two ways of generating the code for your metamodel. The first
one is to use a MTL generator (in ``/generator``) and the second one is to use a
dedicated command line tool written in Python, using Pymultigen, Jinja and PyEcore.

Using the Accelo/MTL Generator
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use this generator, you need Eclipse and the right Acceleo plugins. Once
Eclipse is installed with the right plugins, you need to create a new Acceleo
project, copy the  PyEcore generator in it, configure a new Acceleo runner,
select your ``.ecore`` and your good to go. There is plenty of documentation
over the Internet for Acceleo/MTL project creation/management...

**WARNING:** the Acceleo generator is now deprecated, use pyecoregen instead!

Using the Dedicated CLI Generator (PyEcoregen)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For simple generation, the Acceleo generator will still do the job, but for more
complex metamodel and a more robust generation, pyecoregen is significantly better.
Its use is the prefered solution for the static metamodel code generation.
Advantages over the Acceleo generator are the following:

* it gives the ability to deal with generation from the command line,
* it gives the ability to launch generation programmatically (and very simply),
* it introduces into PyEcore a framework for code generation,
* it allows you to code dedicated behavior in mixin classes,
* it can be installed from `pip`.

This generator source code can be found at this address with mode details:
https://github.com/pyecore/pyecoregen and is available on Pypi, so you can
install it quite symply using:

.. code-block:: bash

    $ pip install pyecoregen

This will automatically install all the required dependencies and give you a new
CLI tool: ``pyecoregen``.

Using this tool, your static code generation is very simple:

.. code-block:: bash

    $ pyecoregen -e your_ecore_file.ecore -o your_output_path

The generated code is automatically formatted using ``autopep8``. Once the code
is generated, your can import it and use it in your Python code.


Manually defines static ``EClass``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To manually defines static ``EClass``, it is simply a matter of creating a
Python class, and adding to it the ``@EMetaclass`` class decorator. This
decorator will automatically add the righ metaclass to the defined class, and
introduce the missing classes in it's inheritance tree. Defining simple
metaclass is thus fairly easy:

.. code-block:: python

    @EMetaclass
    class Person(object):
        name = EAttribute(eType=EString)
        age = EAttribute(eType=EInt)
        children = EReference(upper=-1, containment=True)

        def __init__(self, name):
            self.name = name

    Person.children.eType = Person  # As the relation is reflexive, it must be set AFTER the metaclass creation

    p1 = Person('Parent')
    p1.children.append(Person('Child'))


Without more information, all the created metaclass will be added to a default
``EPackage``, generated on the fly. If the ``EPackage`` must be controlled, a
global variable of ``EPackage`` type, named ``eClass``, must be created in the
module.

.. code-block:: python

    eClass = EPackage(name='pack', nsURI='http://pack/1.0', nsPrefix='pack')

    @EMetaclass
    class TestMeta(object):
        pass

    assert TestMeta.eClass.ePackage is eClass

However, when ``@EMetaclass`` is used, the direct ``super()`` call in
the ``__init__`` constructor cannot be directly called. Instead,
``super(x, self)`` must be called:

.. code-block:: python

    class Stuff(object):
        def __init__(self):
            self.stuff = 10


    @EMetaclass
    class A(Stuff):
        def __init__(self, tmp):
            super(A, self).__init__()
            self.tmp = tmp


    a = A()
    assert a.stuff == 10

If you want to directly extends the PyEcore metamodel, the ``@EMetaclass`` is
not required, and ``super()`` can be used.

.. code-block:: python

    class MyNamedElement(ENamedElement):
        def __init__(self, tmp=None, **kwargs):
            super().__init__(**kwargs)
            self.tmp = tmp


Static/Dynamic ``EOperation``
=============================

PyEcore also support ``EOperation`` definition for static and dynamic metamodel.
For static metamodel, the solution is simple, a simple method with the code is
added inside the defined class. The corresponding ``EOperation`` is created on
the fly. Theire is still some "requirements" for this. In order to be understood
as an ``EOperation`` candidate, the defined method must have at least one
parameter and the first parameter must always be named ``self``.

For dynamic metamodels, the simple fact of adding an ``EOperation`` instance in
the ``EClass`` instance, adds an "empty" implementation:

.. code-block:: python

    >>> import pyecore.ecore as Ecore
    >>> A = Ecore.EClass('A')
    >>> operation = Ecore.EOperation('myoperation')
    >>> param1 = Ecore.EParameter('param1', eType=Ecore.EString, required=True)
    >>> operation.eParameters.append(param1)
    >>> A.eOperations.append(operation)
    >>> a = A()
    >>> help(a.myoperation)
    Help on method myoperation:

    myoperation(param1) method of pyecore.ecore.A instance
    >>> a.myoperation('test')
    ...
    NotImplementedError: Method myoperation(param1) is not yet implemented

For each ``EParameter``, the ``required`` parameter express the fact that the
parameter is required or not in the produced operation:

.. code-block:: python

    >>> operation2 = Ecore.EOperation('myoperation2')
    >>> p1 = Ecore.EParameter('p1', eType=Ecore.EString)
    >>> operation2.eParameters.append(p1)
    >>> A.eOperations.append(operation2)
    >>> a = A()
    >>> a.operation2(p1='test')  # Will raise a NotImplementedError exception

You can then create an implementation for the eoperation and link it to the
EClass:

.. code-block:: python

    >>> def myoperation(self, param1):
    ...     print(self, param1)
    ...
    >>> A.python_class.myoperation = myoperation

To be able to propose a dynamic empty implementation of the operation, PyEcore
relies on Python code generation at runtime.


Notifications
=============

PyEcore gives you the ability to listen to modifications performed on an
element. The ``EObserver`` class provides a basic observer which can receive
notifications from the ``EObject`` it is register in:

.. code-block:: python

    >>> import library as lib  # we use the wikipedia library example
    >>> from pyecore.notification import EObserver, Kind
    >>> smith = lib.Writer()
    >>> b1 = lib.Book()
    >>> observer = EObserver(smith, notifyChanged=lambda x: print(x))
    >>> b1.authors.append(smith)  # observer receive the notification from smith because 'authors' is eOpposite or 'books'

The ``EObserver`` notification method can be set using a lambda as in the
previous example, using a regular function or by class inheritance:

.. code-block:: python

    >>> def print_notif(notification):
    ...     print(notification)
    ...
    >>> observer = EObserver()
    >>> observer.observe(b1)
    >>> observer.notifyChanged = print_notif
    >>> b1.authors.append(smith)  # observer receive the notification from b1

Using inheritance:

.. code-block:: python

    >>> class PrintNotification(EObserver):
    ...     def __init__(self, notifier=None):
    ...         super().__init__(notifier=notifier)
    ...
    ...     def notifyChanged(self, notification):
    ...         print(notification)
    ...
    ...
    >>> observer = PrintNotification(b1)
    >>> b1.authors.append(smith)  # observer receive the notification from b1

The ``Notification`` object contains information about the performed
modification:

* ``new`` -> the new added value (can be a collection) or ``None`` is remove or unset
* ``old`` -> the replaced value (always ``None`` for collections)
* ``feature`` -> the ``EStructuralFeature`` modified
* ``notifer`` -> the object that have been modified
* ``kind`` -> the kind of modification performed

The different kind of notifications that can be currently received are:

* ``ADD`` -> when an object is added to a collection
* ``ADD_MANY`` -> when many objects are added to a collection
* ``REMOVE`` -> when an object is removed from a collection
* ``SET`` -> when a value is set in an attribute/reference
* ``UNSET`` -> when a value is removed from an attribute/reference


Deep Journey Inside PyEcore
===========================

This section will provide some explanation of how PyEcore works.

EClasse Instances as Factories
------------------------------

The most noticeable difference between PyEcore and Java-EMF implementation is
the fact that there is no factories (as you probably already seen). Each EClass
instance is in itself a factory. This allows you to do this kind of tricks:

.. code-block:: python

    >>> A = EClass('A')
    >>> eobject = A()  # We create an A instance
    >>> eobject.eClass
    <EClass name="A">
    >>> eobject2 = eobject.eClass()  # We create another A instance
    >>> assert isinstance(eobject2, eobject.__class__)
    >>> from pyecore.ecore import EcoreUtils
    >>> assert EcoreUtils.isinstance(eobject2, A)


In fact, each EClass instance create a new Python ``class`` named after the
EClass name and keep a strong relationship towards it. Moreover, EClass
implements is a ``callable`` and each time ``()`` is called on an EClass
instance, an instance of the associated Python ``class`` is created. Here is a
small example:

.. code-block:: python

    >>> MyClass = EClass('MyClass')  # We create an EClass instance
    >>> type(MyClass)
    pyecore.ecore.EClass
    >>> MyClass.python_class
    pyecore.ecore.MyClass
    >>> myclass_instance = MyClass()  # MyClass is callable, creates an instance of the 'python_class' class
    >>> myclass_instance
    <pyecore.ecore.MyClass at 0x7f64b697df98>
    >>> type(myclass_instance)
    pyecore.ecore.MyClass
    # We can access the EClass instance from the created instance and go back
    >>> myclass_instance.eClass
    <EClass name="MyClass">
    >>> assert myclass_instance.eClass.python_class is MyClass.python_class
    >>> assert myclass_instance.eClass.python_class.eClass is MyClass
    >>> assert myclass_instance.__class__ is MyClass.python_class
    >>> assert myclass_instance.__class__.eClass is MyClass
    >>> assert myclass_instance.__class__.eClass is myclass_instance.eClass


The Python class hierarchie (inheritance tree) associated to the EClass instance

.. code-block:: python

    >>> B = EClass('B')  # in complement, we create a new B metaclass
    >>> list(B.eAllSuperTypes())
    []
    >>> B.eSuperTypes.append(A)  # B inherits from A
    >>> list(B.eAllSuperTypes())
    {<EClass name="A">}
    >>> B.python_class.mro()
    [pyecore.ecore.B,
     pyecore.ecore.A,
     pyecore.ecore.EObject,
     pyecore.ecore.ENotifier,
     object]
    >>> b_instance = B()
    >>> assert isinstance(b_instance, A.python_class)
    >>> assert EcoreUtils.isinstance(b_instance, A)


Importing an Existing XMI Metamodel/Model
=========================================

XMI support is still a little rough on the edges, but the XMI import is on good tracks.
Currently, only basic XMI metamodel (``.ecore``) and model instances can be
loaded:

.. code-block:: python

    >>> from pyecore.resources import ResourceSet, URI
    >>> rset = ResourceSet()
    >>> resource = rset.get_resource(URI('path/to/mm.ecore'))
    >>> mm_root = resource.contents[0]
    >>> rset.metamodel_registry[mm_root.nsURI] = mm_root
    >>> # At this point, the .ecore is loaded in the 'rset' as a metamodel
    >>> resource = rset.get_resource(URI('path/to/instance.xmi'))
    >>> model_root = resource.contents[0]
    >>> # At this point, the model instance is loaded!

The ``ResourceSet/Resource/URI`` will evolve in the future. At the moment, only
basic operations are enabled: ``create_resource/get_resource/load/save...``.


Dynamic Metamodels Helper
-------------------------

Once a metamodel is loaded from an XMI metamodel (from a ``.ecore`` file), the
metamodel root that is gathered is an ``EPackage`` instance. To access each
``EClass`` from the loaded resource, a ``getEClassifier(...)`` call must be
performed:

.. code-block:: python

    >>> #...
    >>> resource = rset.get_resource(URI('path/to/mm.ecore'))
    >>> mm_root = resource.contents[0]
    >>> A = mm_root.getEClassifier('A')
    >>> a_instance = A()

When a big metamodel is loaded, this operation can be cumbersome. To ease this
operation, PyEcore proposes an helper that gives a quick access to each
``EClass`` contained in the ``EPackage`` and its subpackages. This helper is the
``DynamicEPackage`` class. Its creation is performed like so:

.. code-block:: python

    >>> #...
    >>> resource = rset.get_resource(URI('path/to/mm.ecore'))
    >>> mm_root = resource.contents[0]
    >>> from pyecore.utils import DynamicEPackage
    >>> MyMetamodel = DynamicEPackage(mm_root)  # We create a DynamicEPackage for the loaded root
    >>> a_instance = MyMetamodel.A()
    >>> b_instance = MyMetamodel.B()


Adding External Metamodel Resources
-----------------------------------

External resources for metamodel loading should be added in the resource set.
For example, some metamodels use the XMLType instead of the Ecore one.
The resource creation should be done by hand first:

.. code-block:: python

    int_conversion = lambda x: int(x)  # translating str to int durint load()
    String = Ecore.EDataType('String', str)
    Double = Ecore.EDataType('Double', int, 0, from_string=int_conversion)
    Int = Ecore.EDataType('Int', int, from_string=int_conversion)
    IntObject = Ecore.EDataType('IntObject', int, None,
                                from_string=int_conversion)
    Boolean = Ecore.EDataType('Boolean', bool, False,
                              from_string=lambda x: x in ['True', 'true'],
                              to_string=lambda x: str(x).lower())
    Long = Ecore.EDataType('Long', int, 0, from_string=int_conversion)
    EJavaObject = Ecore.EDataType('EJavaObject', object)
    xmltype = Ecore.EPackage()
    xmltype.eClassifiers.extend([String,
                                 Double,
                                 Int,
                                 EJavaObject,
                                 Long,
                                 Boolean,
                                 IntObject])
    xmltype.nsURI = 'http://www.eclipse.org/emf/2003/XMLType'
    xmltype.nsPrefix = 'xmltype'
    xmltype.name = 'xmltype'
    rset.metamodel_registry[xmltype.nsURI] = xmltype

    # Then the resource can be loaded (here from an http address)
    resource = rset.get_resource(HttpURI('http://myadress.ecore'))
    root = resource.contents[0]


Metamodel References by 'File Path'
-----------------------------------

If a metamodel references others in a 'file path' manner (for example, a
metamodel ``A`` had some relationship towards a ``B`` metamodel like this:
``../metamodelb.ecore`` ), PyEcore requires that the ``B`` metamodel is loaded
first and registered against the metamodel path URI like (in the example, against
the ``../metamodelb.ecore`` URI).

.. code-block:: python

    >>> # We suppose that the metamodel A.ecore has references towards B.ecore
    ... # '../../B.ecore'. Path of A.ecore is 'a/b/A.ecore' and B.ecore is '.'
    >>> resource = rset.get_resource(URI('B.ecore'))  # We load B.ecore first
    >>> root = resource.contents[0]
    >>> rset.metamodel_registry['../../B.ecore'] = root  # We register it against the 'file path' uri
    >>> resource = rset.get_resource(URI('a/b/A.ecore'))  # A.ecore now loads just fine


Adding External resources
-------------------------

When a model reference another one, they both need to be added inside the same
ResourceSet.

.. code-block:: python

    rset.get_resource(URI('uri/towards/my/first/resource'))
    resource = rset.get_resource(URI('uri/towards/my/secon/resource'))

If for some reason, you want to dynamically create the resource which is
required for XMI deserialization of another one, you need to create an empty
resource first:

.. code-block:: python

    # Other model is 'external_model'
    resource = rset.create_resource(URI('the/wanted/uri'))
    resource.append(external_model)


Exporting an Existing XMI Resource
==================================

As for the XMI import, the XMI export (serialization) is still somehow very
basic. Here is an example of how you could save your objects in a file:

.. code-block:: python

    >>> # we suppose we have an already existing model in 'root'
    >>> from pyecore.resources.xmi import XMIResource
    >>> from pyecore.resources import URI
    >>> resource = XMIResource(URI('my/path.xmi'))
    >>> resource.append(root)  # We add the root to the resource
    >>> resource.save()  # will save the result in 'my/path.xmi'
    >>> resource.save(output=URI('test/path.xmi'))  # save the result in 'test/path.xmi'


You can also use a ``ResourceSet`` to deal with this:

.. code-block:: python

    >>> # we suppose we have an already existing model in 'root'
    >>> from pyecore.resources import ResourceSet, URI
    >>> rset = ResourceSet()
    >>> resource = rset.create_resource(URI('my/path.xmi'))
    >>> resource.append(root)
    >>> resource.save()


Dealing with JSON Resources
===========================

PyEcore is also able to load/save JSON models/metamodels. The JSON format it uses
tries to be close from the one described in the `emfjson-jackson <https://github.com/emfjson/emfjson-jackson>`_ project.
The way the JSON serialization/deserialization works, on a user point of view,
is pretty much the same than the XMI resources, but as the JSON resource factory
is not loaded by default (for XMI, it is), you have to manually register it
first. The registration can be performed globally or at a ``ResourceSet`` level.
Here is how to register the JSON resource factory for a given ``ResourceSet``.

.. code-block:: python

    >>> from pyecore.resources import ResourceSet
    >>> from pyecore.resources.json import JsonResource
    >>> rset = ResourceSet()  # We have a resource set
    >>> rset.resource_factory['json'] = lambda uri: JsonResource(uri)  # we register the factory for '.json' extensions


And here is how to register the factory at a global level:

.. code-block:: python

    >>> from pyecore.resources import ResourceSet
    >>> from pyecore.resources.json import JsonResource
    >>> ResourceSet.resource_factory['json'] = lambda uri: JsonResource(uri)


Once the resource factory is registered, you can load/save models/metamodels
exactly the same way you would have done it for XMI. Check the XMI section to
see how to load/save resources using a ``ResourceSet``.

**NOTE:** Currently, the Json serialization is performed using the defaut Python
``json`` lib. It means that your PyEcore model is first translated to a huge
``dict`` before the export/import. For huge models, this could implies a memory
and a performance cost.


Deleting Elements
=================

Deleting elements in EMF is still a sensible point because of all the special
model "shape" that can impact the deletion algorithm. PyEcore supports two main
way of deleting elements: one is a real kind of deletion, while the other is
more less direct.

The ``delete()`` method
-----------------------

The first way of deleting element is to use the ``delete()`` method which is
owned by every ``EObject/EProxy``:

.. code-block:: python

    >>> # we suppose we have an already existing element in 'elem'
    >>> elem.delete()

This call is also recursive by default: every sub-object of the deleted element
is also deleted. This behavior is the one by default as a "containment"
reference is a strong constraint.

The behavior of the ``delete()`` method can be confusing when there is many
``EProxy`` in the game. As the ``EProxy`` only gives a partial view of the
object while it is not resolved, the ``delete()`` can only correctly remove
resolved proxies. If a resource or many elements that are referenced in many
other resources must be destroyed, in order to be sure to not introduce broken
proxies, the best solution is to resolve all the proxies first, then to delete
them.


Removing an element from it's container
---------------------------------------

You can also, in a way, removing elements from a model using the XMI
serialization. If you want to remove an element from a Resource, you have to
remove it from its container. PyEcore does not serialize elements that are not
contained by a ``Resource`` and each reference to this 'not-contained' element
is not serialized.

Modifying Elements Using Commands
=================================

PyEcore objects can be modified as shown previously, using basic Python
operators, but these mofifications cannot be undone. To do so, it is required to
use ``Command`` and a ``CommandStack``. Each command represent a basic action
that can be performed on an element (set/add/remove/move/delete):

.. code-block:: python

    >>> from pyecore.commands import Set
    >>> # we assume have a metamodel with an A EClass that owns a 'name' feature
    >>> a = A()
    >>> set = Set(owner=a, feature='name', value='myname')
    >>> if set.can_execute:
    ...     set.execute()
    >>> a.name
    myname

If you use a simple command withtout ``CommandStack``, the ``can_execute`` call
is mandatory! It performs some prior computation before the actual command
execution. Each executed command also supports 'undo' and 'redo':

.. code-block:: python

    >>> if set.can_undo:
    ...     set.undo()
    >>> assert a.name is None
    >>> set.redo()
    >>> assert a.name == 'myname'

As for the ``execute()`` method, the ``can_undo`` call must be done before
calling the ``undo()`` method. However, there is no ``can_redo``, the ``redo()``
call can be mad right away after an undo.

To compose all of these commands, a ``Compound`` can be used. Basically, a
``Compound`` acts as a list with extra methods (``execute``, ``undo``,
``redo``...):

.. code-block:: python

    >>> from pyecore.commands import Compound
    >>> a = A()  # we use a new A instance
    >>> c = Compound(Set(owner=a, feature='name', value='myname'),
    ...              Set(owner=a, feature='name', value='myname2'))
    >>> len(c)
    2
    >>> if c.can_execute:
    ...     c.execute()
    >>> a.name
    myname2
    >>> if c.can_undo:
    ...     c.undo()
    >>> assert a.name is None

In order to organize and keep a stack of each played command, a ``CommandStack``
can be used:

.. code-block:: python

    >>> from pyecore.commands import CommandStack
    >>> a = A()
    >>> stack = CommandStack()
    >>> stack.execute(Set(owner=a, feature='name', value='myname'))
    >>> stack.execute(Set(owner=a, feature='name', value='myname2'))
    >>> stack.undo()
    >>> assert a.name == 'myname'
    >>> stack.redo()
    >>> assert a.name == 'myname2'


Here is a quick review of each command:

* ``Set`` --> sets a ``feature`` to a ``value`` for an ``owner``
* ``Add`` --> adds a ``value`` object to a ``feature`` collection from an ``owner`` object (``Add(owner=a, feature='collection', value=b)``). This command can also add a ``value`` at a dedicated ``index`` (``Add(owner=a, feature='collection', value=b, index=0)``)
* ``Remove`` --> removes a ``value`` object from a ``feature`` collection from an ``owner`` (``Remove(owner=a, feature='collection', value=b)``). This command can also remove an object located at an ``index`` (``Remove(owner=a, feature='collection', index=0)``)
* ``Move`` --> moves a ``value`` to a ``to_index`` position inside a ``feature`` collection (``Move(owner=a, feature='collection', value=b, to_index=1)``). This command can also move an element from a ``from_index`` to a ``to_index`` in a collection (``Move(owner=a, feature='collection', from_index=0, to_index=1)``)
* ``Delete`` --> deletes an elements and its contained elements (``Delete(owner=a)``)


Dynamically Extending PyEcore Base Classes
==========================================

PyEcore is extensible and there is two ways of modifying it: either by extending
the basic concepts (as ``EClass``, ``EStructuralFeature``...), or by directly
modifying the same concepts.

Extending PyEcore Base Classes
------------------------------

To extend the PyEcore base classes, the only thing to do is to create new
``EClass`` instances that have some base classes as ``superclass``.
The following excerpt shows how you can create an ``EClass`` instance that
will add support ``EAnnotation`` to each created instance:

.. code-block:: python

    >>> from pyecore.ecore import *
    >>> A = EClass('A', superclass=(EModelElement.eClass))  # we need to use '.eClass' to stay in the PyEcore EClass instance level
    >>> a = A()  # we create an instance that has 'eAnnotations' support
    >>> a.eAnnotations
    EOrderedSet()
    >>> annotation = EAnnotation(source='testSource')
    >>> annotation.details['mykey'] = 33
    >>> a.eAnnotations.append(annotation)
    >>> EOrderedSet([<pyecore.ecore.EAnnotation object at 0x7fb860a99f28>])

If you want to extend ``EClass``, the process is mainly the same, but there is a
twist:

.. code-block:: python

    >>> from pyecore.ecore import *
    >>> NewEClass = EClass('NewEClass', superclass=(EClass.eClass))  # NewEClass is an EClass instance and an EClass
    >>> A = NewEClass('A')  # here is the twist, currently, EClass instance MUST be named
    >>> a = A()  # we can create 'A' instance
    >>> a
    <pyecore.ecore.A at 0x7fb85b6c06d8>


Modifying PyEcore Base Classes
------------------------------

PyEcore let you dynamically add new features to the base class and thus
introduce new feature for base classes instances:

.. code-block:: python

    >>> from pyecore.ecore import *
    >>> EClass.new_feature = EAttribute('new_feature', EInt)  # EClass has now a new EInt feature
    >>> A = EClass('A')
    >>> A.new_feature
    0
    >>> A.new_feature = 5
    >>> A.new_feature
    5


Dependencies
============

The dependencies required by pyecore are:

* ordered-set which is used for the ``ordered`` and ``unique`` collections expressed in the metamodel,
* lxml which is used for the XMI parsing.

These dependencies are directly installed if you choose to use ``pip``.


Run the Tests
=============

Tests uses `py.test` and 'coverage'. Everything is driven by `Tox`, so in order
to run the tests simply run:

.. code-block:: bash

    $ tox


Liberty Regarding the Java EMF Implementation
=============================================

* There is some meta-property that are not still coded inside PyEcore. More will come with time,
* ``Resource`` can only contain a single root at the moment,
* External resources (like ``http://www.eclipse.org/emf/2003/XMLType``) must be create by hand an loaded in the ``global_registry`` or as a ``resource`` of a ``ResourceSet``,
* Proxies are not "removed" once resolved as in the the Java version, instead they acts as transparent proxies and redirect each calls to the 'proxied' object.

State
=====

In the current state, the project implements:

* the dynamic/static metamodel definitions,
* reflexive API,
* inheritance,
* enumerations,
* abstract metaclasses,
* runtime typechecking,
* attribute/reference creations,
* collections (attribute/references with upper bound set to ``-1``),
* reference eopposite,
* containment reference,
* introspection,
* select/reject on collections,
* Eclipse XMI import (partially, only single root models),
* Eclipse XMI export (partially, only single root models),
* simple notification/Event system,
* EOperations support,
* code generator for the static part,
* EMF proxies (first version),
* object deletion (first version),
* EMF commands (first version),
* EMF basic command stack,
* EMF very basic Editing Domain,
* JSON import (simple JSON format),
* JSON export (simple JSON format).

The things that are in the roadmap:

* new implementation of ``EOrderedSet``, ``EList``, ``ESet`` and ``EBag``,
* new implementation of ``EStringToStringMapEntry`` and ``EFeatureMapEntry``,
* multiple roots models,
* derived collections,
* URI mapper,
* documentation,
* copy/paste (?).

Existing Projects
=================

There is not so much projects proposing to handle model and metamodel in Python.
The only projects I found are:

* PyEMOF (http://www.lifl.fr/~marvie/software/pyemof.html)
* EMF4CPP (https://github.com/catedrasaes-umu/emf4cpp)
* PyEMOFUC (http://www.istr.unican.es/pyemofuc/index_En.html)

PyEMOF proposes an implementation of the OMG's EMOF in Python. The project
targets Python2, only supports Class/Primitive Types (no Enumeration), XMI
import/export and does not provide a reflexion layer. The project didn't move
since 2005.

EMF4CPP proposes a C++ implementation of EMF. This implementation also
introduces Python scripts to call the generated C++ code from a Python
environment. It seems that the EMF4CPP does not provide a reflexive layer
either.

PyEMOFUC proposes, like PyEMOF, a pure Python implementation of the OMG's EMOF.
If we stick to a kind of EMF terminology, PyEMOFUC only supports dynamic
metamodels and seems to provide a reflexive layer. The project does not appear
seems to have moved since a while.

Contributors
============

Thanks for making PyEcore better!

* Mike Pagel (`@moltob <https://github.com/moltob>`_)

Additional Resources
====================

* The article at this address: http://modeling-languages.com/pyecore-python-eclipse-modeling-framework
  gives more information and implementations details about PyEcore.
