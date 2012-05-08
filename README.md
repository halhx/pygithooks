Git pre-commit hooks for Scala code formatting
===============================================

Installation
------------

* Requires Python 2.5+. Not tested with Py3k.
* Requires PyYaml 3.10+ (http://pyyaml.org/)
* Requires cloc 1.53+ (http://cloc.sourceforge.net/)
* Clone this repo & submodules:
  + `git clone git://github.com/halhx/pygithooks.git --recursive`
* Configure as desired (see below).
* If this is the only git hook you are using:
  + `cd <your_repo>`
  + `cd .git`
  + `mv hooks hooks.pygithooks.bak`
  + `ln -s /path/to/pygithooks/hooks hooks`
* If you want to use these hooks along with other hooks, just add `/path/to/pygithooks/hooks/pre-commit.py || exit 1` to your existing `pre-commit`.

Configuration
-------------

Configuration works through [`git config`](http://www.kernel.org/pub/software/scm/git/docs/git-config.html), in the section `pygithooks`.

Sample configuration command:

    git config --global pygithooks.incremental true

Supported keys:

* **incremental**
  + in incremental mode, if a file failed the hooks *before* this commit, allow it through unchecked.
    This is useful in a large codebase that isn't already well-formatted: The hooks make sure that
    files never *become* badly formatted, but don't block development on existing badly formatted files.
  + sample value: `true`
  + default value: `false`
* **incremental.verbose**
  + Print all filenames that were allowed through only because of the `incremental` flag. (Does nothing
    if `incremental` is not enabled.) This is useful for knowing which files should (eventually) be cleaned up.
  + sample value: `true`
  + default value: `false`
* **debug**
  + print some debug goo during processing. Handy for figuring out why pygithooks is not behaving as you expect.
    Don't leave this on. :)
  + sample value: `true`
  + default value: `false`

Contributing
------------
* Yes, please. Fork and send a pull request!


License
-------
* `pygithooks` is released under the BSD license.
* `reindent.py` is bundled for ease of installation; it is in the public domain. See the top of `hooks/reindent.py` for details.
* `pep8.py` is included as a submodule. It is under the expat license. See the top of `hooks/pep8/pep8.py` for details.
