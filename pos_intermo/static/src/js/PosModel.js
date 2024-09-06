odoo.define('pos_intermo.PosModel', function(require) {
    'use strict';

    const models = require('point_of_sale.models');
    const { Gui } = require('point_of_sale.Gui');
    const IntermoKeyScreen = require('pos_intermo.IntermoKeyScreen');

    // Extend the POS model to insert the new screen in the workflow
    models.PosModel = models.PosModel.extend({
        showIntermoKeyScreen: function() {
            // Function to show the custom screen
            Gui.showScreen('IntermoKeyScreen');
        },

        initialize: function() {
            this._super.apply(this, arguments);
            // Show the new screen before the payment success screen
            this.showIntermoKeyScreen();
        },
    });

    return models.PosModel;
});
