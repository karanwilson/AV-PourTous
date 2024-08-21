import Home from './Home.vue';

frappe.provide('frappe.PourTous');

frappe.PourTous.pourtous = class {
    constructor({ parent }) {
        console.log("inside pourtous constructor");
        this.$parent = $(document);
        this.page = parent.page;
        this.make_body();
    }
    make_body() {
        console.log("inside pourtous make_body");
        this.$el = this.$parent.find('.main-section');
        this.vue = new Vue({
            vuetify: new Vuetify({
                rtl: frappe.utils.is_rtl(),
                theme: {
                    themes: {
                        light: {
                            background: '#FFFFFF',
                            primary: '#0097A7',
                            secondary: '#00BCD4',
                            accent: '#9575CD',
                            success: '#66BB6A',
                            info: '#2196F3',
                            warning: '#FF9800',
                            error: '#E86674',
                            orange: '#E65100',
                            golden: '#A68C59',
                            badge: '#F5528C',
                            customPrimary: '#085294',
                        },
                    },
                },
            }),
            el: this.$el[0],
            data: {},
            render: h => h(Home),
        });
    }
    setup_header() {}
};
