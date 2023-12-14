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
    generated_komisi = fields.Boolean('Komisi Generated', compute='compute_generated_komisi', store=True)
    agen_id = fields.Many2one('res.users', string='Agen')
    komisi_line_ids = fields.One2many('account.move', 'komisi_id', string='Komisi Line')
    komisi_id = fields.Many2one('account.move', string='Komisi', ondelete='set null')
    komisi_inv_count = fields.Integer('Count Invoice', compute='count_invoice_komisi')

    @api.depends('komisi_id')
    def compute_generated_komisi(self):
        for rec in self:
            if not rec.komisi_id:
                rec.generated_komisi = False
    

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
        
    
    # def generate_komisi(self):

    #     def kalkulasi_komisi(total):
    #         result = {}
    #         price = 0
    #         if total >= 1 and total <= 15:
    #             price = 750000
    #         elif total >= 16 and total <= 30:
    #             price = 1250000
    #         elif total >= 31:
    #             price = 1500000

    #         result['pax'] = total
    #         result['price'] = price

    #         return result

    #     source_orders = self.line_ids.sale_line_ids.order_id
    #     if not source_orders:
    #         raise UserError('Tidak ada Sale Order')
        
    #     total_komisi = {}
    #     # cids = []
    #     if len(source_orders) > 1:
    #         for so in source_orders:
    #             seller = so.user_id
    #             agen = self.agen_id
    #             if seller and agen:
    #                 total_jamaah = len(self.jamaah_ids.filtered(lambda sel: sel.user_id.id == seller.id))
    #                 total_komisi[seller.id] = kalkulasi_komisi(total_jamaah)
    #             else:
    #                 raise UserError('Tidak ada Penjual atau Agen')

    #         kloter = self.invoice_line_ids.filtered(lambda r: r.product_id.categ_id.is_kloter == True)
    #         if len(kloter) > 1:
    #             kloter = kloter[0]

    #         created = self.env['account.move'].create({
    #             'move_type': 'in_invoice',
    #             'partner_id': self.partner_id.id,
    #             'agen_id': agen.id,
    #             'komisi_id': self.id,
    #             'invoice_date': date.today(),
    #             'date': date.today(),
    #             'jamaah_ids': [(6, 0, self.jamaah_ids.ids)],
    #         })

    #         for k,v in total_komisi.items():
    #             created.invoice_line_ids : [(0, 0, {
    #                 'name': "Komisi %s" % (self.env['res.users'].browse(k).name),
    #                 'product_id': kloter.product_id.id if kloter else False,
    #                 'quantity': v['pax'],
    #                 'price_unit': v['price'],
    #             })]

    #             # cids.append(created)
            
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'name': 'Vendor Bill',
    #             'res_model': 'account.move',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'target': 'current',
    #             'res_id': created.id,
    #             # 'domain': [('id', 'in', cids)],
    #         }
            
    #     else:
    #         seller = source_orders.user_id
    #         agen = self.agen_id
    #         if seller and agen:
    #             total_jamaah = len(self.jamaah_ids.filtered(lambda sel: sel.user_id.id == seller.id))
    #             if total_jamaah > 0:
    #                 komisi = kalkulasi_komisi(total_jamaah)
    #                 kloter = self.invoice_line_ids.filtered(lambda r: r.product_id.categ_id.is_kloter == True)
    #                 if len(kloter) > 1:
    #                     kloter = kloter[0]

    #                 created = self.env['account.move'].create({
    #                     'move_type': 'in_invoice',
    #                     'partner_id': self.partner_id.id,
    #                     'agen_id': agen.id,
    #                     'komisi_id': self.id,
    #                     'invoice_date': date.today(),
    #                     'date': date.today(),
    #                     'invoice_line_ids': [(0, 0, {
    #                         'product_id': kloter.product_id.id if kloter else False,
    #                         'name': "Komisi %s" % (agen.name),
    #                         'quantity': komisi['pax'],
    #                         'price_unit': komisi['price'],
    #                     })],
    #                     'jamaah_ids': [(6, 0, self.jamaah_ids.ids)],
    #                 })

    #                 return {
    #                     'type': 'ir.actions.act_window',
    #                     'name': 'Vendor Bill',
    #                     'res_model': 'account.move',
    #                     'view_type': 'form',
    #                     'view_mode': 'form',
    #                     'target': 'current',
    #                     'res_id': created.id,
    #                 }
                
    #             else:
    #                 raise UserError('Tidak ada Jamaah dari %s' % seller.name)
    #         else:
    #             raise UserError('Tidak ada Penjual atau Agen')
            
            