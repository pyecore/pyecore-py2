from .ecore import EcoreUtils, EReference, EObject
from .notification import Notification, Kind
from .ordered_set_patch import ordered_set


class BadValueError(TypeError):
    def __init__(self, got=None, expected=None):
        msg = "Expected type {0}, but got type {1} with value {2} instead"
        msg = msg.format(expected, type(got).__name__, got)
        super(BadValueError, self).__init__(msg)


class PyEcoreValue(object):
    def __init__(self, owner, efeature):
        super(PyEcoreValue, self).__init__()
        self._owner = owner
        self._efeature = efeature

    def check(self, value):
        if not EcoreUtils.isinstance(value, self._efeature.eType):
            raise BadValueError(value, self._efeature.eType)

    def _update_container(self, value, previous_value=None):
        if not isinstance(self._efeature, EReference):
            return
        if not self._efeature.containment:
            return
        if isinstance(value, EObject):
            object.__setattr__(value, '_container', self._owner)
            object.__setattr__(value, '_containment_feature', self._efeature)
        elif previous_value:
            object.__setattr__(previous_value, '_container', value)
            object.__setattr__(previous_value, '_containment_feature', value)


class EValue(PyEcoreValue):
    def __init__(self, owner, efeature):
        super(EValue, self).__init__(owner, efeature)
        self._value = efeature.get_default_value()

    def _get(self):
        return self._value

    def _set(self, value, update_opposite=True):
        self.check(value)
        previous_value = self._value
        self._value = value
        owner = self._owner
        efeature = self._efeature
        notif = Notification(old=previous_value,
                             new=value,
                             feature=efeature,
                             kind=Kind.UNSET if value is None else Kind.SET)
        owner.notify(notif)
        owner._isset.add(efeature)

        if not isinstance(efeature, EReference):
            return
        self._update_container(value, previous_value)
        if not update_opposite:
            return

        # if there is no opposite, we set inverse relation and return
        if not efeature.eOpposite:
            couple = (owner, efeature)
            if hasattr(value, '_inverse_rels'):
                if hasattr(previous_value, '_inverse_rels'):
                    previous_value._inverse_rels.remove(couple)
                value._inverse_rels.add(couple)
            elif value is None and hasattr(previous_value, '_inverse_rels'):
                previous_value._inverse_rels.remove(couple)
            return

        eOpposite = efeature.eOpposite
        # if we are in an 'unset' context
        if value is None:
            if previous_value is None:
                return
            if eOpposite.many:
                object.__getattribute__(previous_value, eOpposite.name) \
                      .remove(owner, update_opposite=False)
            else:
                object.__setattr__(previous_value, eOpposite.name, None)
        else:
            previous_value = value.__getattribute__(eOpposite.name)
            if eOpposite.many:
                value.__getattribute__(eOpposite.name) \
                     .append(owner, update_opposite=False)
            else:
                # We disable the eOpposite update
                value.__dict__[eOpposite.name]. \
                      _set(owner, update_opposite=False)


class ECollection(PyEcoreValue):
    @staticmethod
    def create(owner, feature):
        if feature.ordered and feature.unique:
            return EOrderedSet(owner, feature)
        elif feature.ordered and not feature.unique:
            return EList(owner, feature)
        elif feature.unique:
            return ESet(owner, feature)
        else:
            return EBag(owner, feature)  # see for better implem

    def __init__(self, owner, efeature):
        super(ECollection, self).__init__(owner, efeature)

    def _get(self):
        return self

    def _update_opposite(self, owner, new_value, remove=False):
        if not isinstance(self._efeature, EReference):
            return
        eOpposite = self._efeature.eOpposite
        if not eOpposite:
            couple = (new_value, self._efeature)
            if remove and couple in owner._inverse_rels:
                owner._inverse_rels.remove(couple)
            else:
                owner._inverse_rels.add(couple)
            return

        if eOpposite.many and not remove:
            owner.__getattribute__(eOpposite.name).append(new_value, False)
        elif eOpposite.many and remove:
            owner.__getattribute__(eOpposite.name).remove(new_value, False)
        else:
            new_value = None if remove else new_value
            owner.__getattribute__(eOpposite.name)  # Force load
            owner.__dict__[eOpposite.name] \
                 ._set(new_value, update_opposite=False)

    def remove(self, value, update_opposite=True):
        self._update_container(None, previous_value=value)
        if update_opposite:
            self._update_opposite(value, self._owner, remove=True)
        super(ECollection, self).remove(value)
        self._owner.notify(Notification(old=value,
                                        feature=self._efeature,
                                        kind=Kind.REMOVE))

    def insert(self, i, y):
        self.check(y)
        self._update_container(y)
        self._update_opposite(y, self._owner)
        super(ECollection, self).insert(i, y)
        self._owner.notify(Notification(new=y,
                                        feature=self._efeature,
                                        kind=Kind.ADD))
        self._owner._isset.add(self._efeature)

    def pop(self, index=None):
        if index is None:
            value = super(ECollection, self).pop()
        else:
            value = super(ECollection, self).pop(index)
        self._update_container(None, previous_value=value)
        self._update_opposite(value, self._owner, remove=True)
        self._owner.notify(Notification(old=value,
                                        feature=self._efeature,
                                        kind=Kind.REMOVE))
        return value

    def clear(self):
        [self.remove(x) for x in set(self)]

    def select(self, f):
        return [x for x in self if f(x)]

    def reject(self, f):
        return [x for x in self if not f(x)]

    def __iadd__(self, items):
        if ordered_set.is_iterable(items):
            self.extend(items)
        else:
            self.append(items)
        return self


class EList(ECollection, list):
    def __init__(self, owner, efeature=None):
        super(EList, self).__init__(owner, efeature)

    def append(self, value, update_opposite=True):
        self.check(value)
        self._update_container(value)
        if update_opposite:
            self._update_opposite(value, self._owner)
        super(EList, self).append(value)
        self._owner.notify(Notification(new=value,
                                        feature=self._efeature,
                                        kind=Kind.ADD))
        self._owner._isset.add(self._efeature)

    def extend(self, sublist):
        for x in sublist:
            self.check(x)
        for value in sublist:
            self._update_container(value)
            self._update_opposite(value, self._owner)
        super(EList, self).extend(sublist)
        self._owner.notify(Notification(new=sublist,
                                        feature=self._efeature,
                                        kind=Kind.ADD_MANY))
        self._owner._isset.add(self._efeature)

    def __setslice__(self, i, j, y):
        is_collection = ordered_set.is_iterable(y)
        if is_collection:
            sliced_elements = self.__getslice__(i, j)
            for element in y:
                self.check(element)
                self._update_container(element)
                self._update_opposite(element, self._owner)
            # We remove (not really) all element from the slice
            for element in sliced_elements:
                self._update_container(None, previous_value=element)
                self._update_opposite(element, self._owner, remove=True)
            if sliced_elements and len(sliced_elements) > 1:
                self._owner.notify(Notification(old=sliced_elements,
                                                feature=self._efeature,
                                                kind=Kind.REMOVE_MANY))
            elif sliced_elements:
                self._owner.notify(Notification(old=sliced_elements[0],
                                                feature=self._efeature,
                                                kind=Kind.REMOVE))
        super(EList, self).__setslice__(i, j, y)
        kind = Kind.ADD
        if is_collection and len(y) > 1:
            kind = Kind.ADD_MANY
        elif is_collection:
            y = y[0] if y else y
        self._owner.notify(Notification(new=y,
                                        feature=self._efeature,
                                        kind=kind))
        self._owner._isset.add(self._efeature)

    def __setitem__(self, i, y):
        is_collection = ordered_set.is_iterable(y)
        self.check(y)
        self._update_container(y)
        self._update_opposite(y, self._owner)
        super(EList, self).__setitem__(i, y)
        kind = Kind.ADD
        if is_collection and len(y) > 1:
            kind = Kind.ADD_MANY
        elif is_collection:
            y = y[0] if y else y
        self._owner.notify(Notification(new=y,
                                        feature=self._efeature,
                                        kind=kind))
        self._owner._isset.add(self._efeature)


class EBag(EList):
    pass


class EAbstractSet(ECollection):
    def __init__(self, owner, efeature=None):
        super(EAbstractSet, self).__init__(owner, efeature)
        self._orderedset_update = False

    def append(self, value, update_opposite=True):
        self.add(value, update_opposite)

    def add(self, value, update_opposite=True):
        self.check(value)
        self._update_container(value)
        if update_opposite:
            self._update_opposite(value, self._owner)
        super(EAbstractSet, self).add(value)
        if not self._orderedset_update:
            self._owner.notify(Notification(new=value,
                                            feature=self._efeature,
                                            kind=Kind.ADD))
        self._owner._isset.add(self._efeature)

    def extend(self, sublist):
        self.update(sublist)

    def update(self, others):
        for x in others:
            self.check(x)
        for value in others:
            self._update_container(value)
            self._update_opposite(value, self._owner)
        super(EAbstractSet, self).update(others)
        self._owner.notify(Notification(new=others,
                                        feature=self._efeature,
                                        kind=Kind.ADD_MANY))
        self._owner._isset.add(self._efeature)


class EOrderedSet(EAbstractSet, ordered_set.OrderedSet):
    def __init__(self, owner, efeature=None):
        super(EOrderedSet, self).__init__(owner, efeature)
        ordered_set.OrderedSet.__init__(self)

    def update(self, others):
        self._orderedset_update = True
        super(EOrderedSet, self).update(others)
        self._orderedset_update = False


class ESet(EOrderedSet):
    pass
