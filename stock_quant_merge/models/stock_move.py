# -*- coding: utf-8 -*-
# © 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _do_unreserve(self):
        for move in self:

            quants = self.env['stock.quant']._gather(
                move.product_id, move.location_id, strict=False)
            reserved_quants = quants.filtered(lambda q: q.reserved_quantity > 0)
            super(StockMove, move). _do_unreserve()
            if (
                    reserved_quants and
                    not self.env.context.get('disable_stock_quant_merge')):
                reserved_quants.merge_stock_quants()
