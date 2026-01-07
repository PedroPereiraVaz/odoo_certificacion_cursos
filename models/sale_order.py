from odoo import models, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        """ Override to check for blockchain variants and entitle users. """
        res = super(SaleOrder, self)._action_confirm()

        for order in self:
            for line in order.order_line:
                # 1. Check if product is linked to any Course (Channel)
                # Robust approach: We search for the channel directly. 
                # If the product is linked to a course, we will find it.
                # We avoid checking specific product fields like 'detailed_type' which caused issues.
                
                product_tmpl_id = line.product_id.product_tmpl_id.id
                channels = self.env['slide.channel'].search([
                    ('product_id', '=', product_tmpl_id)
                ])
                
                if channels:
                    
                    # 2. Check for Blockchain Attribute
                    # We assume attribute name "Certification" and value "Blockchain" 
                    # OR we can just check a tag or specific attribute value ID.
                    # Best universal way: Check if the variant has a value containing "Blockchain" (Simple)
                    # or better: Define this on the product template settings or config.
                    # Per plan: Using Variant.
                    
                    is_blockchain_variant = False
                    # Check attributes
                    for val in line.product_id.product_template_variant_value_ids:
                         if "blockchain" in val.name.lower():
                             is_blockchain_variant = True
                             break
                    
                    if is_blockchain_variant:
                         for channel in channels:
                             if channel.blockchain_certification_active:
                                 # Find partner membership
                                 # website_slides logic creates membership on invoice payment usually (if paid)
                                 # or on confirm if free.
                                 # We need to ensure we catch the partner.
                                 # order.partner_id might be the buyer, but attendee could be different?
                                 # Assuming buyer = attendee for now (standard flow).
                                 
                                 slide_partner = self.env['slide.channel.partner'].search([
                                     ('channel_id', '=', channel.id),
                                     ('partner_id', '=', order.partner_id.id)
                                 ], limit=1)
                                 
                                 if slide_partner:
                                     slide_partner.blockchain_certification_entitled = True
        return res
