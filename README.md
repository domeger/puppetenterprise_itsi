Splunk ITSI Module for Puppet Enterprise
[![Build Status](https://travis-ci.org/domeger/SplunkTAforPuppetEnterprise.svg?branch=master)](https://travis-ci.org/domeger/SplunkTAforPuppetEnterprise)
======

Documentation
-------------
The Splunk ITSI Module for Puppet Enterprise requires that you have the following installed:

[**Splunk Enterprise 6.4+**](https://www.spunk.com)
[**Splunk ITSI 2.4x**](https://www.spunk.com)
[**Puppet Enterprise 2017.1.1+**](https://www.puppet.com)


Installation
------------

**Method: #1**

#### Install via Splunk Package

First, you'll need to export a Splunk Package by cloning the repo and exporting
the contents.

```
$ git clone https://github.com/domeger/puppetenterprise_itsi.git puppetenterprise_itsi
$ cd puppetenterprise_itsi
$ git archive \
    --format=tar.gz \
    --prefix=puppetenterprise_itsi/ \
    --output=puppetenterprise_itsi.tar.gz \
    HEAD
$ mv puppetenterprise_itsi.tar.gz puppetenterprise_itsi.spl
```

After exporting the Splunk Package `.spl`, you can install the package using
Splunk's built-in Apps page.

1. Select "Manage Apps" from the Apps dropdown.
1. Select the "Install app from file" button.
1. Select the generated `puppetenterprise_itsi.spl` package.
1. Splunk will walk you through all required setup.

External Resource: Splunk GUI Installation Interface - [Splunk Documentation - Install App](https://docs.splunk.com/Documentation/AddOns/released/Overview/Distributedinstall "Splunk Docs")


**Method: #2**

#### Install via Git Clone

You can install the git repository directly into your Splunk app contents and
keep the scripts updated.

```
$ export SPLUNK_HOME="/path/to/Splunk"
$ cd $SPLUNK_HOME/etc/apps
$ git clone https://github.com/domeger/puppetenterprise_itsi.git puppetenterprise_itsi
```

Restart Splunk after cloning the repository, then open the Setup page from the
Manage Apps page to configure your Puppet Enterprise server info. From the Manage Apps page
you can also enable and disable the Puppet Enterprise Addon for Splunk.


Developing and Contributing
---------------------------
The Splunk ITSI Module for Puppet Enterprise requires Splunk 6.4+ + Splunk ITSI 2.4x + Splunk Addon Builder 2.0+ in order to properly add new features or bug fixes. Please refer to the [Splunk Documentation - Addon Builder](https://docs.splunk.com/Documentation/AddonBuilder/2.2.0/UserGuide/Importandexport) on how to use Git to develop and push your changes to this repo as a branch and following the standard code review process. 

License
-------

See [LICENSE](LICENSE) file.

Support
-------

Are you a Splunk + Puppet customer who enjoys sharing knowledge and want to put some great feature into an opensource project. We encourage you to submit issues and pull request so that we can make this Technical Addon better and help the community as a whole get better insight to their Puppet Enterprise deployments.

Feel free to leave comments or questions. We are here to make this community project more adaptive to all types of use cases.
