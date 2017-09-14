"""
    Some common module library includes
"""
import sys
from splunk.clilib.bundle_paths import make_splunkhome_path

sys.path.append(make_splunkhome_path(['etc', 'apps', 'SA-ITOA', 'lib']))

from lib.ITOA.itoa_common import add_to_sys_path
from ITOA.setup_logging import setup_logging

# Add lib path to import paths for packages
add_to_sys_path([make_splunkhome_path(['etc', 'apps', 'puppetenterprise_itsi', 'lib'])])
