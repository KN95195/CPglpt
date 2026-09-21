<script setup lang="ts">
defineProps<{src?:string;alt:string;large?:boolean}>()
</script>
<template><div class="visual" :class="{large}"><img :src="src||'/assets/product-radar.png'" :alt="alt"></div></template>
<style scoped>
.visual{display:grid;place-items:center;width:100%;height:100%;overflow:hidden;background:#eef6ff;color:#5796e8;border:1px solid #dce9f8}.visual img{display:block;width:100%;height:100%;max-width:100%;max-height:100%;object-fit:contain;object-position:center;padding:10px;box-sizing:border-box}
</style>
