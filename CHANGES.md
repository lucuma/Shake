# Changes


## Version 1.2.0

- New Rails-like internationalization framework.  Available at `app.i18n` or as {{ t('key_name', **kwargs) }} in the templates.

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

