<script setup>
// 1. Import the necessary component from vue-router.
import { RouterView } from 'vue-router';

// In a standard setup, you would typically have a Navigation component here as well, 
// which uses RouterLink to navigate between pages (e.g., Home, RSVP, Gallery).
// However, since WelcomeView is the only page and has its own internal navigation, 
// we keep App.vue minimal.
</script>

<template>
    <!-- 
        The <RouterView /> component renders the component corresponding to the current route.
        Since you configured '/' to load WelcomeView, this tag will display your wedding page.
    -->
    <RouterView />
</template>

<style>
/* Optional: Global base styles for the application */
</style>