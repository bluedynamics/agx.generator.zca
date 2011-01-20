The ``profiles`` directory contains the generator related UML profile(s).

The convention is to provide an ``agx.core.interfaces.IProfileLocation``
utility for each profile by a unique name and provide the related profile in
``eggstructur/package/profiles/some.profile.uml``. The utility itself has
2 Attributes. ``name``, which is the profile name, in this example
``some_profile.uml`` and ``package``, which is a reference to the related
package.