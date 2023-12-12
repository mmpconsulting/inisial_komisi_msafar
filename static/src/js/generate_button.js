/** @odoo-module inisial_komisi_msafar */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
export class GenerateKomisiListController extends ListController {
   setup() {
       super.setup();
   }
   OnClickKomisi() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'generate.komisi.wizard',
          name:'New Komisi',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
      });
   }
}
registry.category("views").add("generate_komisi_button_tree", {
   ...listView,
   Controller: GenerateKomisiListController,
   buttonTemplate: "button_generate_komisi.ListView.Buttons",
});