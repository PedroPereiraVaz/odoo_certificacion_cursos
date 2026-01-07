from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    blockchain_certification_active = fields.Boolean(
        string="Blockchain Certification Active",
        help="If checked, allows selling blockchain-certified variants of this course."
    )
    
    blockchain_cost = fields.Monetary(
        string="Blockchain Certificate Cost",
        currency_field='currency_id',
        default=0.0,
        help="Extra cost for the Blockchain Certified variant."
    )
    
    company_id = fields.Many2one(
        'res.company', 
        string='Company', 
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency', 
        related='company_id.currency_id',
        readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        channels = super(SlideChannel, self).create(vals_list)
        for channel in channels:
            if channel.blockchain_certification_active:
                channel._sync_product_variants()
        return channels

    def write(self, vals):
        res = super(SlideChannel, self).write(vals)
        if 'blockchain_certification_active' in vals or 'blockchain_cost' in vals:
            for channel in self:
                if channel.blockchain_certification_active:
                    channel._sync_product_variants()
        return res

    def _sync_product_variants(self):
        """ 
        Automatically configures the Product Template to have 
        'Certification Type' attribute with 'Standard' and 'Blockchain' values.
        Sets the extra price on the 'Blockchain' value.
        """
        self.ensure_one()
        if not self.product_id:
            return

        product_tmpl = self.product_id.product_tmpl_id
        
        # 1. Ensure Attribute Exists
        attrib_name = "Certificate Type"
        attribute = self.env['product.attribute'].search([
            ('name', '=', attrib_name),
            ('create_variant', '=', 'always') # Ensure variants are created
        ], limit=1)
        
        if not attribute:
            attribute = self.env['product.attribute'].create({
                'name': attrib_name,
                'create_variant': 'always',
                'display_type': 'radio',
            })
            
        # 2. Ensure Values Exist
        val_standard = self.env['product.attribute.value'].search([('attribute_id', '=', attribute.id), ('name', '=', 'Standard')], limit=1)
        if not val_standard:
            val_standard = self.env['product.attribute.value'].create({'attribute_id': attribute.id, 'name': 'Standard'})
            
        val_blockchain = self.env['product.attribute.value'].search([('attribute_id', '=', attribute.id), ('name', '=', 'Blockchain')], limit=1)
        if not val_blockchain:
            val_blockchain = self.env['product.attribute.value'].create({'attribute_id': attribute.id, 'name': 'Blockchain'})

        # 3. Add to Product Template
        # Check if line exists
        ptal = self.env['product.template.attribute.line'].search([
            ('product_tmpl_id', '=', product_tmpl.id),
            ('attribute_id', '=', attribute.id)
        ], limit=1)
        
        if not ptal:
            ptal = self.env['product.template.attribute.line'].create({
                'product_tmpl_id': product_tmpl.id,
                'attribute_id': attribute.id,
                'value_ids': [(6, 0, [val_standard.id, val_blockchain.id])]
            })
        else:
            # Ensure both values are present
            ptal.write({'value_ids': [(4, val_standard.id), (4, val_blockchain.id)]})

        # 4. Set Extra Price
        # Extra prices are stored on `product.template.attribute.value` (ptav) 
        # which links the line and the value.
        
        # Standard: 0
        ptav_std = ptal.product_template_value_ids.filtered(lambda v: v.product_attribute_value_id == val_standard)
        if ptav_std:
            ptav_std.price_extra = 0.0
            
        # Blockchain: Cost
        ptav_bc = ptal.product_template_value_ids.filtered(lambda v: v.product_attribute_value_id == val_blockchain)
        if ptav_bc:
            ptav_bc.price_extra = self.blockchain_cost
