# Shake Changelog

## Version 1.5

- Added a `wrapper` parameter to `shake.templates.link_to` for making navigations bootstrap-style.

- User roles in the default project skeleton, and other changes.


## Version 1.4

- New pluggable session interface system.

- Dropped the Werkzeug provided 'secure cookie' as session system. Using the `itsdangerous` library instead.  Motivations:
    1. the implementation comes from the django signing module and was heavily reviewed in terms of the crypto used.
    2. it uses JSON instead of pickle, so it is inmune to pickle's vulnerabilities if in some way the SECRET_KEY is exposed.
    3. it does not rely on Python specifics so your proxy server could be able to read it.

- New `AuditableMixin` in the common bundle of the default skeleton. Use it to get automatic `created_at` and `modified_at` columns.


## Version 1.3

- Perfect requirements and settings structure.

- `get_env` and `set_env` search from/set the environment variable `SHAKE_ENV` if no `.SHAKE_ENV` file is present. This is useful for deploying with services like Heroku.

- i18n module extracted to a separated library (now named `AllSpeak`).

- jQuery (bundled with the default skeleton) updated to version 1.8.


## Version 1.2.5

- Added `get_timezone` method to `shake.Request`.


## Version 1.2.4

- Respect the default timezone if a custom one is not defined.

- Several minor bugfixes to the default project template.

- Adds a `partial` argument to `link_to` to matching partial URLs.


## Version 1.2.3

- Several bugfixes to `Request` class.


## Version 1.2.2

- Added PyYaml to the requirements (removed by mistake).

- Fix the class name generation (when adding a bundle).


## Version 1.2.1

- Adds the `i18n.format` method, that formats the value according to the detected data type.

- Added tests for the i18n module.

- Important bugfixes to the i18n module.


## Version 1.2.0

- New Rails-like internationalization solution.  Available at `app.i18n` or as {{ t('key_name', **kwargs) }} in the templates.

- Auto-created `Render` instance at `app.render`.  Uses the `'<app-path>/templates/'` folder by default.

- A static folder is added by default at `'/static/ -> <app-path>/static/'` if `DEBUG=True` and no other static paths are defined.

- `Shake` must be now instantiated with ``__file__'` as the first argument. Example:

    app = Shake(__file__, settings)

  this is used to calculate the templates, locales and static folders.

- The environment setting is now loaded from the `.SHAKE_ENV` file instead from the `manage.py` script (it was unreliable for multiple `manage.py` scripts).  If the files is not found, `Shake.get_env` return `'development'` by default.  `Shake.set_env` create that file if it doesn't exists or overwrites it.

- The `manage.py` in the default project now includes `Solution`'s fixtures related functions.

- The word `'templates'` is now used instead of `'views'`, and `'views'` is now used instead of `'controllers'`.

- Added a new template global function: `link_to` makes easier to create HTML anchor element for navigation, that are marked as "active" when visiting a particular URL.

- General refactoring of the code.

