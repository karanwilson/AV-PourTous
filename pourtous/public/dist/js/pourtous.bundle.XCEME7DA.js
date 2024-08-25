(()=>{var R={},h=function(){var t=this,s=t.$createElement,n=t._self._c||s;return n("h1",[t._v("Pour Tous")])},b=[];h._withStripped=!0;var I=void 0,T=void 0,j=void 0,k=!1;function F(t,s,n,i,a,d,o,l,c,_){let e=(typeof n=="function"?n.options:n)||{};return e.__file="../pourtous/pourtous/public/js/pourtous/components/Navbar.vue",e.render||(e.render=t.render,e.staticRenderFns=t.staticRenderFns,e._compiled=!0,a&&(e.functional=!0)),e._scopeId=i,e}var A=F({render:h,staticRenderFns:b},I,R,T,k,j,!1,void 0,void 0,void 0),x=A;var E={},g=function(){var t=this,s=t.$createElement,n=t._self._c||s;return n("h1",[t._v("Hello")])},N=[];g._withStripped=!0;var w=void 0,P=void 0,U=void 0,O=!1;function V(t,s,n,i,a,d,o,l,c,_){let e=(typeof n=="function"?n.options:n)||{};return e.__file="../pourtous/pourtous/public/js/pourtous/components/PourTous.vue",e.render||(e.render=t.render,e.staticRenderFns=t.staticRenderFns,e._compiled=!0,a&&(e.functional=!0)),e._scopeId=i,e}var B=V({render:g,staticRenderFns:N},w,E,P,O,U,!1,void 0,void 0,void 0),y=B;var X={data:()=>({page:"PourTous"}),components:{Navbar:x,PourTous:y},methods:{setPage(t){this.page=t},remove_frappe_nav(){this.$nextTick(()=>{$(".page-head").remove(),$(".navbar.navbar-default.navbar-fixed-top").remove()})}},mounted(){this.remove_frappe_nav()},created:function(){setTimeout(()=>{this.remove_frappe_nav()},1e3)}},S=function(){var t=this,s=t.$createElement,n=t._self._c||s;return n("v-app",{staticClass:"container1"},[n("v-main",[n("Navbar",{on:{changePage:function(i){return t.setPage(i)}}}),t._v(" "),n(t.page,{tag:"component",staticClass:"mx-4 md-4"})],1)],1)},H=[];S._withStripped=!0;var M=function(t){!t||t("data-v-552741a8_0",{source:`
.container1[data-v-552741a8] {
    margin-top: 0px;
}
`,map:{version:3,sources:["../pourtous/pourtous/public/js/pourtous/Home.vue"],names:[],mappings:";AAiDA;IACA,eAAA;AACA",file:"Home.vue",sourcesContent:[`<template>
    <v-app class="container1">
        <v-main>
            <Navbar @changePage="setPage($event)"></Navbar>
            <component v-bind:is="page" class="mx-4 md-4"></component>
        </v-main>
    </v-app>
</template>

<script>
import Navbar from './components/Navbar.vue';
import PourTous from './components/PourTous.vue';

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

    mounted() {
        this.remove_frappe_nav();
    },

    created: function () {
        setTimeout(() => {
            this.remove_frappe_nav();
        }, 1000);
    }
};
<\/script>

<style scoped>
.container1 {
    margin-top: 0px;
}
</style>`]},media:void 0})},z="data-v-552741a8",D=void 0,L=!1;function W(t,s,n,i,a,d,o,l,c,_){let e=(typeof n=="function"?n.options:n)||{};e.__file="../pourtous/pourtous/public/js/pourtous/Home.vue",e.render||(e.render=t.render,e.staticRenderFns=t.staticRenderFns,e._compiled=!0,a&&(e.functional=!0)),e._scopeId=i;{let u;if(s&&(u=o?function(r){s.call(this,_(r,this.$root.$options.shadowRoot))}:function(r){s.call(this,l(r))}),u!==void 0)if(e.functional){let r=e.render;e.render=function(f,p){return u.call(p),r(f,p)}}else{let r=e.beforeCreate;e.beforeCreate=r?[].concat(r,u):[u]}}return e}function m(){let t=m.styles||(m.styles={}),s=typeof navigator!="undefined"&&/msie [6-9]\\b/.test(navigator.userAgent.toLowerCase());return function(i,a){if(document.querySelector('style[data-vue-ssr-id~="'+i+'"]'))return;let d=s?a.media||"default":i,o=t[d]||(t[d]={ids:[],parts:[],element:void 0});if(!o.ids.includes(i)){let l=a.source,c=o.ids.length;if(o.ids.push(i),s&&(o.element=o.element||document.querySelector("style[data-group="+d+"]")),!o.element){let _=document.head||document.getElementsByTagName("head")[0],e=o.element=document.createElement("style");e.type="text/css",a.media&&e.setAttribute("media",a.media),s&&(e.setAttribute("data-group",d),e.setAttribute("data-next-index","0")),_.appendChild(e)}if(s&&(c=parseInt(o.element.getAttribute("data-next-index")),o.element.setAttribute("data-next-index",c+1)),o.element.styleSheet)o.parts.push(l),o.element.styleSheet.cssText=o.parts.filter(Boolean).join(`
`);else{let _=document.createTextNode(l),e=o.element.childNodes;e[c]&&o.element.removeChild(e[c]),e.length?o.element.insertBefore(_,e[c]):o.element.appendChild(_)}}}}var q=W({render:S,staticRenderFns:H},M,X,z,L,D,!1,m,void 0,void 0),C=q;frappe.provide("frappe.PourTous");frappe.PourTous.pourtous=class{constructor({parent:t}){this.$parent=$(document),this.page=t.page,this.make_body()}make_body(){this.$el=this.$parent.find(".main-section"),this.vue=new Vue({vuetify:new Vuetify({rtl:frappe.utils.is_rtl(),theme:{themes:{light:{background:"#FFFFFF",primary:"#0097A7",secondary:"#00BCD4",accent:"#9575CD",success:"#66BB6A",info:"#2196F3",warning:"#FF9800",error:"#E86674",orange:"#E65100",golden:"#A68C59",badge:"#F5528C",customPrimary:"#085294"}}}}),el:this.$el[0],data:{},render:t=>t(C)})}setup_header(){}};})();
//# sourceMappingURL=pourtous.bundle.XCEME7DA.js.map
