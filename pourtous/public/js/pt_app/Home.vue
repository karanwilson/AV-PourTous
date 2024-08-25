<template>
    <v-app class="container1">
        <v-main>
            <Navbar @changePage="setPage($event)"></Navbar>
            <component v-bind:is="page" class="mx-4 md-4"></component>
        </v-main>
    </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue';
import PourTous from './components/pourtous/PourTous.vue';

export default {
    data: () => {
        return {
            page: 'PourTous'
        };
    },

    components: {
        Navbar, PourTous
    },

    methods: {
        setPage(page) {
            this.page = page;
        },
        remove_frappe_nav() {
            this.$nextTick(() => {
                $('.page-head').remove();
                $('.navbar.navbar-default.navbar-fixed-top').remove();
            });
        }
    },
    /*
    mounted() {
        this.remove_frappe_nav();
    },

    created: function () {
        setTimeout(() => {
            this.remove_frappe_nav();
        }, 1000);
    }
    */
};
</script>

<style scoped>
.container1 {
    margin-top: 0px;
}
</style>