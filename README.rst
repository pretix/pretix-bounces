Bounce processing for pretix
============================

This is a plugin for `pretix`_. Once installed and configured, it makes pretix use random ``Sender`` headers
for emails like ``noreply-amCwRFatawEjetS8@pretix.eu`` for outgoing emails. The ``From`` and ``Reply-To``
headers remain untouched. It then periodically checks for emails in a specified IMAP inbox and adds replied
emails to the log of an order. This leads to an automatic logging of bounces on pretix-level.

Configuration
-------------

This requires an additional section in the ``pretix.cfg`` config file that looks like this::

    [bounces]
    alias=noreply-%s@mydomain.com
    from_domain=mydomain.com
    server=mail.mydomain.com:993
    user=noreply@mydomain.com
    pass=12345678

The plugin will only be effective for mails sent through the system default mailer (specified in the same file), not
for events with a custom SMTP server.

Development setup
-----------------

1. Make sure that you have a working `pretix development setup`_.

2. Clone this repository, eg to ``local/pretix-bounces``.

3. Activate the virtual environment you use for pretix development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretix's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretix server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------

Copyright 2017 Raphael Michel

Released under the terms of the Apache License 2.0


.. _pretix: https://github.com/pretix/pretix
.. _pretix development setup: https://docs.pretix.eu/en/latest/development/setup.html
