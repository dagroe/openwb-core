<script>
import { useMqttStore } from "@/stores/mqtt.js";

export default {
  name: "WelcomeView",
  data() {
    return {
      mqttStore: useMqttStore(),
    };
  },
  mounted() {
    setTimeout(this.selectFirstRoute, 3000);
  },
  methods: {
    selectFirstRoute() {
      if (this.mqttStore.getDefaultView) {
        this.$router.push({ name: this.mqttStore.getDefaultView });
      } else {
        console.warn("no router view enabled, check your configuration!");
      }
    },
  },
};
</script>

<template>
  <i-container>
    <i-row
      center
      middle
    >
      <i-column>
        <i-card color="primary">
          <template #header>
            Cards Theme
          </template>
          <img
            class="logo"
            src="/openWB_logo_dark.png"
          >
        </i-card>
      </i-column>
    </i-row>
  </i-container>
</template>

<style scoped>
.container,
.row {
  height: 100vh;
}

.card {
  ----background: inherit !important;
  ----body--color: var(--contrast-color-for-dark-background) !important;
}

img.logo {
  max-width: 100%;
}
</style>
