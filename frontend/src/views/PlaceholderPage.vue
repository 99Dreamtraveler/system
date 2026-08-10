<template><section class="placeholder-page"><el-card class="placeholder-card" shadow="never"><el-icon class="placeholder-icon" :size="34"><component :is="icon" /></el-icon><h2>{{ title }}</h2><p>{{ description }}</p></el-card></section></template>
<script setup>
import { DataBoard } from '@element-plus/icons-vue'
defineProps({ title:{type:String,required:true}, description:{type:String,required:true}, icon:{type:[Object,Function],default:DataBoard} })
</script>
<style scoped>
.placeholder-page{min-height:calc(100vh - 108px);display:grid;place-items:center}.placeholder-card{width:min(100%,680px);padding:52px 32px;text-align:center;border-radius:var(--radius-md);background:var(--bg-card);border-color:var(--border-color)}.placeholder-icon{color:var(--accent);margin-bottom:18px}h2{margin-bottom:10px;color:var(--text-primary);font-size:22px}p{color:var(--text-secondary);font-size:14px;line-height:1.8}
</style>
