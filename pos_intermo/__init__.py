# Import models, controllers, and other components of the module
from . import models
# from . import controllers
# from . import wizards  # Uncomment if you have wizard files

# You can also include any other initialization code here, such as loading custom configurations.


from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(env):
    setup_provider(env, 'intermo')


def uninstall_hook(env):
    reset_payment_provider(env, 'intermo')