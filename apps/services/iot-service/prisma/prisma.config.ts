import { defineConfig } from '@prisma/internals'

export default defineConfig({
  datasource: {
    url: process.env.DATABASE_URL
  }
})
