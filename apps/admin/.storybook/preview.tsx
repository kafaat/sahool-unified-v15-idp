import type { Preview } from '@storybook/react';
import '../src/app/globals.css';

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: 'centered',
    // RTL support
    direction: 'rtl',
  },
  decorators: [
    (Story) => (
      <div dir="rtl" lang="ar" className="font-sans">
        <Story />
      </div>
    ),
  ],
};

export default preview;
