<template>
    <v-app class="container1">
        <v-main>
            <Navbar @changePage="setPage($event)"></Navbar>
            <component v-bind:id="page" class="mx-4 md-4"></component>
        </v-main>
    </v-app>
</template>

<script setup>
import { reactive, onMounted } from 'vue';
import Navbar from './components/Navbar.vue';
import PourTous from './components/PourTous.vue';

const data = reactive({
    page: 'PourTous'
});

setPage((page) => {
    this.page = page;
});

remove_frappe_nav(() => {
    this.$nextTick(() => {
        $('.page-head').remove();
        $('.navbar.navbar-default.navbar-fixed-top').remove();
    });
});

onMounted(() => {
    this.remove_frappe_nav();
});

setTimeout(() => {
    this.remove_frappe_nav();
}, 1000);

</script>