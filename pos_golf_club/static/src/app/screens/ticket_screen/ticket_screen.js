/** @odoo-module **/
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";

patch(TicketScreen.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.orm = useService("orm");
    },
    async printGolfCard() {
        let order = this.getSelectedOrder() || this.pos.get_order() || null;
        const orderId = order.id;
        let golf_card_ids = order.golf_card_ids;
        if (!golf_card_ids || golf_card_ids.length ==0) {
            const domain = [['pos_order_id','=',orderId]];
            golf_card_ids = await this.orm.search("golf.card", domain);
            console.debug("TicketScreen printGolfCard orm golf_card_ids",golf_card_ids,domain);
        }
        return await this.actionService.doAction("golf_club.action_golf_card_report", {
            additionalContext: {
                active_ids: golf_card_ids,
            },
        });
    }
});
