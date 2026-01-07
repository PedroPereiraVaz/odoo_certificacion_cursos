from odoo import models, fields

class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    blockchain_certification_entitled = fields.Boolean(
        string="Entitled to Blockchain Cert",
        default=False,
        help="If True, the user purchased the blockchain version of the course."
    )
