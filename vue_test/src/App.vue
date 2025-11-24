<template>
  <router-view></router-view>
  <MessageHost />
</template>

<script>
import MessageHost from './components/MessageHost.vue'

export default {
  name: 'App',
  components: { MessageHost }
}
</script>

<style>
body {
  font-family: Arial, sans-serif;
  background-color: #f0f2f5;
  margin: 0;
  padding: 0;
}
</style>