# -*- coding: utf-8 -*-
# © 2015 OdooMRP team
# © 2015 AvanzOSC
# © 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.multi
    def _mergeable_domain(self):
        """Return the quants which may be merged with the current record"""
        self.ensure_one()
        return [('id', '!=', self.id),
                ('product_id', '=', self.product_id.id),
                ('lot_id', '=', self.lot_id.id),
                ('package_id', '=', self.package_id.id),
                ('location_id', '=', self.location_id.id),
                ('reserved_quantity', '!=', 0)]

    @api.multi
    def merge_stock_quants(self):
        # Get a copy of the recordset
        pending_quants = self.browse(self.ids)
        for quant2merge in self.filtered(lambda q: q.reserved_quantity > 0):
            if quant2merge in pending_quants:
                quants = self.search(quant2merge._mergeable_domain())
                for quant in quants:
                    if (quant2merge._get_latest_move_line() == quant._get_latest_move_line()):
                        quant2merge.sudo().quantity += quant.quantity
                        quant2merge.sudo().reserved_quantity += quant.reserved_quantity
                        pending_quants -= quant
                        quant.with_context(force_unlink=True).sudo().unlink()

    @api.multi
    def _get_latest_move_line(self):
        move_lines = self.env['stock.move.line'].search([
            ('product_id', '=', self.product_id.id),
            '|',
            ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_id.id),
            ('lot_id', '=', self.lot_id.id),
            '|',
            ('package_id', '=', self.package_id.id),
            ('result_package_id', '=', self.package_id.id),
        ])
        latest = []
        if move_lines:
            latest = move_lines[0]
        return latest
