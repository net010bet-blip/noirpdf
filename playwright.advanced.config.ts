import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests/e2e',testMatch:'advanced.spec.ts',timeout:90000,use:{baseURL:process.env.E2E_BASE_URL||'http://localhost:4200',headless:true},workers:1,reporter:'list'});
