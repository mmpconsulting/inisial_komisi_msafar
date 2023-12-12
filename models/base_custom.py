from odoo import _, api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    jamaah_ids = fields.Many2many('res.partner', string='Jamaah')

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    jamaah_ids = fields.Many2many('res.partner', string='Jamaah')