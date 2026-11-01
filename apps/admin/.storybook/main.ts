import type { StorybookConfig } from '@storybook/nextjs';
import path from 'path';

// Storybook's plugins use the installed Webpack. Select that same compiler
// for Next's preset so its parser hooks match the plugins. This configuration
// runs only in Storybook; it does not change production Next.js builds.
process.env.NEXT_PRIVATE_LOCAL_WEBPACK = 'true';

const config: StorybookConfig = {
  stories: ['../src/components/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
  ],
  framework: {
    name: '@storybook/nextjs',
    options: {},
  },
  staticDirs: ['../public'],
  webpackFinal: async (config) => {
    if (config.resolve) {
      config.resolve.alias = {
        ...config.resolve.alias,
        '@': path.resolve(__dirname, '../src'),
      };
    }
    return config;
  },
};

export default config;
