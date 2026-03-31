/** @odoo-module **/
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component } from "@odoo/owl";

export class GolfScorecardWidget extends Component {
    static template = "golf_club.ScorecardTemplate";
    static props = { ...standardFieldProps };

    _getSectionHandicap(records, playerHcp) {
        if (!playerHcp) return 0;
        // Calculamos cuántos golpes caen en este set de registros
        // Un hoyo recibe un golpe si su handicap es <= hándicap del jugador
        // (Para hándicaps > 18, un hoyo puede recibir 2 golpes si HCP + 18 <= playerHcp)
        return records.reduce((sum, r) => {
            let strokes = 0;
            const holeHcp = r.data.handicap || 0;
            if (holeHcp <= playerHcp) strokes++;
            if (holeHcp + 18 <= playerHcp) strokes++;
            return sum + strokes;
        }, 0);
    }

    get scorecardData() {
        console.log("scorecardData props",this.props);
        const list = this.props.record.data[this.props.name];
        console.log("scorecardData list",list);
        const playerHcp = this.props.record.data.player_handicap || 0; 
        if (!list || !list.records) {
            return { frontNine: [], backNine: [], frontGross: 0, backGross: 0, frontNet: 0, backNet: 0, totalGross: 0, totalNet: 0 };
        }

        const records = list.records.sort((a, b) => a.data.hole_number - b.data.hole_number);
        const frontNine = records.filter(r => r.data.hole_number <= 9);
        const backNine = records.filter(r => r.data.hole_number > 9);
        
        const frontGross = frontNine.reduce((sum, r) => sum + (r.data.score || 0), 0);
        const backGross = backNine.reduce((sum, r) => sum + (r.data.score || 0), 0);

        const frontHcpStrokes = this._getSectionHandicap(frontNine, playerHcp);
        const backHcpStrokes = this._getSectionHandicap(backNine, playerHcp);

        return {
            frontNine,
            backNine,
            frontGross,
            backGross,
            frontNet: frontGross - frontHcpStrokes,
            backNet: backGross - backHcpStrokes,
            totalGross: frontGross + backGross,
            totalNet: (frontGross + backGross) - playerHcp
        };
    }
        
    async onScoreChange(record, event) {
        const value = parseInt(event.target.value) || 0;
        await record.update({ score: value });
    }
}

registry.category("fields").add("golf_card_widget", {
    component: GolfScorecardWidget,
    supportedTypes: ["one2many"],
});
