{
    'name': 'Blockchain Course Certification',
    'version': '18.0.1.0.0',
    'summary': 'Certify Odoo eLearning Courses on Blockchain',
    'description': """
        Integrates Odoo eLearning with Blockchain Core.
        - Adds 'Blockchain Certification' option to Courses.
        - Enables 'Blockchain Entitlement' via Product Variants.
        - Automates Blockchain Registration upon Survey Certification (PDF).
        - Supports Revocation and Traceability.
    """,
    'category': 'Website/eLearning',
    'author': 'Antigravity',
    'depends': [
        'website_slides',
        'website_sale_slides', # Important for sale flow
        'survey',
        'sale',
        'odoo_blockchain_core'
    ],
    'data': [
        'views/slide_channel_views.xml',
        'views/slide_channel_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
