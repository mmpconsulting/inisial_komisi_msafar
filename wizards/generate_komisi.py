from odoo import _, api, fields, models
from odoo.exceptions import UserError
from operator import itemgetter
from datetime import date

class GenerateKomisiWizard(models.TransientModel):
    _name = 'generate.komisi.wizard'
    _description = 'Generate Komisi'

    agen_id = fields.Many2one('res.users', string='Agen')
    product_id = fields.Many2one('product.template', string='Kloter')
    account_id = fields.Many2one('account.account', string='Akun')

    def query_invoices(self):
        products = self.product_id.product_variant_ids
        query_prd = ''
        if len(products) == 1:
            query_prd = "line.product_id = %s" % products.id
        elif len(products) > 1:
            query_prd = "line.product_id in %s" % str(tuple(products.ids))

        self._cr.execute("""
        SELECT move.id as invoice
        FROM account_move_line as line
        LEFT JOIN account_move as move on line.move_id = move.id
        WHERE 
            %s and 
            move.agen_id = %s and
            move.state = 'posted' and
            (move.is_komisi = false or move.is_komisi is null) and
            (move.generated_komisi = false or move.generated_komisi is null)
        GROUP BY move.id
        """ % (query_prd, self.agen_id.id))
        res = self._cr.dictfetchall()
        return res
    
    def kalkulasi_komisi(self, total):
        com_rate = self.env['commision.rate'].search([('min','<=',total),('max','>=',total)], limit=1)
        if not com_rate:
            raise UserError('Tidak ada tarif komisi')
        result = {}
        price = com_rate.rate if com_rate else 0

        result['pax'] = total
        result['price'] = price

        return result

    def generate_komisi(self):
        self = self.sudo()
        raw_inv = self.query_invoices()

        if raw_inv:
            invoices = list(map(itemgetter('invoice'), raw_inv))
        else:
            raise UserError('Tidak ada Invoice / Faktur dari agen %s' % self.agen_id.name)

        all_invoices = self.env['account.move'].browse(invoices)
        jamaah = all_invoices.mapped('jamaah_ids')
        total_jamaah = len(jamaah)

        total_komisi = self.kalkulasi_komisi(total_jamaah)
        created = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.agen_id.partner_id.id if self.agen_id.partner_id else all_invoices[-1].partner_id.id,
            'agen_id': self.agen_id.id,
            'is_komisi': True,
            'invoice_date': date.today(),
            'date': date.today(),
            'invoice_line_ids': [(0, 0, {
                # 'product_id': self.product_id.id,
                'account_id': self.account_id.id,
                'name': "Komisi %s" % (self.agen_id.name),
                'quantity': total_komisi['pax'],
                'price_unit': total_komisi['price'],
            })],
            'jamaah_ids': [(6, 0, jamaah.ids)],
        })

        all_invoices.write({
            'generated_komisi': True,
            'komisi_id': created.id
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Komisi',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'res_id': created.id,
            # 'domain': [('id', 'in', cids)],
        }