import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests/e2e',testMatch:'pages.spec.ts',timeout:60000,use:{headless:true},workers:1,reporter:'list'});
