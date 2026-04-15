import type { Meta, StoryObj } from '@storybook/react';
import AlertBadge from './AlertBadge';

const meta: Meta<typeof AlertBadge> = {
  title: 'UI/AlertBadge',
  component: AlertBadge,
  tags: ['autodocs'],
  argTypes: {
    severity: {
      control: 'select',
      options: ['low', 'medium', 'high', 'critical'],
    },
    locale: {
      control: 'select',
      options: ['ar', 'en'],
    },
  },
};
export default meta;

type Story = StoryObj<typeof AlertBadge>;

export const Low: Story = {
  args: { severity: 'low', locale: 'ar' },
};

export const Medium: Story = {
  args: { severity: 'medium', locale: 'ar' },
};

export const High: Story = {
  args: { severity: 'high', locale: 'ar' },
};

export const Critical: Story = {
  args: { severity: 'critical', locale: 'ar' },
};

export const AllSeverities: Story = {
  render: () => (
    <div className="flex items-center gap-3">
      <AlertBadge severity="low" />
      <AlertBadge severity="medium" />
      <AlertBadge severity="high" />
      <AlertBadge severity="critical" />
    </div>
  ),
};
