    // NOTE: Need redirect_to_custom_setup=1 to override ui_visible=false
    //       in Splunk Light 6.2.
    // JIRA: Workaround lack of API to build URLs that are agnostic
    //       to the root endpoint location and locale. (SPL-91659)
    var PATH_TO_ROOT = '../../../../..';
    window.location = PATH_TO_ROOT + '/manager/puppetenterprise_itsi/apps/local/puppetenterprise_itsi/setup?action=edit';
