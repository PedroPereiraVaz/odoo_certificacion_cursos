import base64
import hashlib
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SurveyUserInput(models.Model):
    _name = 'survey.user_input'
    _inherit = ['survey.user_input', 'blockchain.certified.mixin']

    def _compute_blockchain_hash(self):
        """ 
        Implementation of abstract method.
        Gets the PDF attachment of the certification and hashes it.
        """
        self.ensure_one()
        
        # 1. Find the generated PDF attachment
        # Odoo usually names it "Certification - [User] - [Survey].pdf" or similar
        # But reliable link is via res_model/res_id
        domain = [
            ('res_model', '=', 'survey.user_input'),
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/pdf')
        ]
        
        # Sort by latest to get the newest generated one
        attachment = self.env['ir.attachment'].search(domain, order='create_date desc', limit=1)
        
        if not attachment:
            # Attempt to FORCE generation if missing
            if hasattr(self, '_generate_certification_report'):
                # This method might not be public in all versions, need care.
                # In standard Odoo, printing the certification generates it.
                # Let's try to call the report action mechanism
                report = self.env.ref('survey.certification_report')
                pdf_content, _ = report._render_qweb_pdf(self.ids)
                
                # We should save it to ensure consistency? 
                # Ideally, we create the attachment so we hash what is stored.
                attachment = self.env['ir.attachment'].create({
                    'name': f"Certification - {self.partner_id.name or 'Guest'}.pdf",
                    'type': 'binary',
                    'datas': base64.b64encode(pdf_content),
                    'res_model': 'survey.user_input',
                    'res_id': self.id,
                    'mimetype': 'application/pdf'
                })
            else:
                return False

        if not attachment or not attachment.datas:
            return False

        # 2. Hash the binary data
        raw_data = base64.b64decode(attachment.datas)
        return hashlib.sha256(raw_data).hexdigest()

    def _check_blockchain_entitlement(self):
        """ Verify if user bought the blockchain version """
        # Link is: Survey -> Slide Channel Partner -> Slide Channel -> Product
        # survey.user_input has 'slide_partner_id' if linked to course.
        if self.slide_partner_id and self.slide_partner_id.blockchain_certification_entitled:
            return True
        return False

    def write(self, vals):
        """ Hook for status changes """
        res = super(SurveyUserInput, self).write(vals)
        
        for record in self:
            # 1. Registration Hook: Scoring Success
            if 'scoring_success' in vals and vals['scoring_success']:
                if record._check_blockchain_entitlement():
                     # Ensure PDF exists before registering
                     # We might need to delay this slightly or ensure report gen happens first.
                     # Calling register will trigger _compute_blockchain_hash which fixes PDF.
                     try:
                        record.action_blockchain_register()
                     except Exception as e:
                         # Don't block flow, just log
                         # _logger.error...
                         pass

            # 2. Revocation Hook: If manually set to failed or active=False?
            # Or dedicated action. For now, let's respect the Mixin's manual action.
            # But if someone "Un-certifies" (e.g. scoring_success = False), should we revoke?
            # That might be dangerous if accidental.
            # Better to rely on manual 'action_blockchain_revoke' from the button.
            pass
            
        return res
