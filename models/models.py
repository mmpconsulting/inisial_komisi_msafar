from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import date

class CommisionRate(models.Model):
    _name = 'commision.rate'
    _description = 'Commision Rate'
    _order = "min"

    min = fields.Integer('Min')
    max = fields.Integer('Max')
    rate = fields.Float('Rate')
    

class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'
    
    def _create_invoices(self, sale_orders):
        res = super(SaleAdvancePaymentInv, self)._create_invoices(sale_orders)
        agen = self.sale_order_ids.agen_id
        res.update({
            'agen_id': agen.id if agen else False,
            'jamaah_ids': [(6, 0, self.sale_order_ids.jamaah_ids.ids)],
        })
        return res
        

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    is_kloter = fields.Boolean('Kloter', default=False)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    agen_id = fields.Many2one('res.users', string='Agen', ondelete='restrict')

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_komisi = fields.Boolean('Komisi', default=False)
    generated_komisi = fields.Boolean('Komisi Generated', default=False)
    agen_id = fields.Many2one('res.users', string='Agen')
    komisi_line_ids = fields.One2many('account.move', 'komisi_id', string='Komisi Line')
    komisi_id = fields.Many2one('account.move', string='Komisi', ondelete='set default')
    komisi_inv_count = fields.Integer('Count Invoice', compute='count_invoice_komisi')

    def unlink(self):
        for rec in self:
            if rec.komisi_line_ids:
                for kom in rec.komisi_line_ids:
                    kom.generated_komisi = False
        return super(AccountMove, self).unlink()

    @api.depends('komisi_line_ids')
    def count_invoice_komisi(self):
        for rec in self:
            rec.komisi_inv_count = len(self.komisi_line_ids)

    def view_komisi_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'res_model': 'account.move',
            'view_type': 'tree,form',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', self.komisi_line_ids.ids)],
            'context' : {'create' : False, 'edit': False, 'delete': False},
        }

    def view_komisi(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Komisi',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': self.komisi_id.id,
            'context' : {'create' : False, 'edit': False, 'delete': False},
        }
        